from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from django.utils.dateparse import parse_datetime
from traffic.forms import LocationForm, RoadSegmentForm, CongestionTypeForm, TrafficForm
from traffic.models import Location, RoadSegment, CongestionType, Traffic
import random

def serialize_road_segment(road):
    traffic = getattr(road, 'traffic', None)
    coefficient = traffic.congestion_type.time_coefficient if traffic else 1.0
    return {
        'id': road.id,
        'point_a_id': road.point_a.id,
        'point_a_name': road.point_a.name,
        'point_b_id': road.point_b.id,
        'point_b_name': road.point_b.name,
        'distance_km': road.distance_km,
        'coefficient': coefficient,
    }

def serialize_traffic(traffic):
    return {
        'road_segment_id': traffic.road_segment.id,
        'road_name': str(traffic.road_segment),
        'congestion_type_id': traffic.congestion_type.id,
        'congestion_type_name': traffic.congestion_type.name,
        'time_coefficient': traffic.congestion_type.time_coefficient,
        'last_updated': traffic.last_updated.isoformat(),
    }

def create_crud_handler(model, form_class, template_base, serialize_func=None):
    def handler(request, pk=None):
        if request.method == 'GET' and pk is None and (
            request.GET.get('format') == 'json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        ):
            if serialize_func is not None:
                queryset = model.objects.all()
                if model == RoadSegment:
                    queryset = queryset.select_related('point_a', 'point_b', 'traffic__congestion_type')
                elif model == Traffic:
                    queryset = queryset.select_related('road_segment', 'congestion_type')
                data = [serialize_func(obj) for obj in queryset]
            else:
                data = list(model.objects.all().values())
            return JsonResponse(data, safe=False)

        if pk is not None and request.path.endswith('/delete/'):
            obj = get_object_or_404(model, pk=pk)
            if request.method == 'POST':
                obj.delete()
                return redirect(f'{template_base}s')
            return render(request, 'traffic/delete.html', {
                'object': obj,
                'type': model.__name__,
                'cancel_url': f'{template_base}_detail',
                'cancel_id': obj.id,
            })

        if (pk is not None and request.path.endswith('/update/')) or request.path.endswith('/create/'):
            is_update = pk is not None and request.path.endswith('/update/')
            obj = get_object_or_404(model, pk=pk) if is_update else None
            if request.method == 'POST':
                form = form_class(request.POST, instance=obj)
                if form.is_valid():
                    saved_obj = form.save()
                    if is_update:
                        return redirect(f'{template_base}_detail', pk=saved_obj.pk)
                    else:
                        return redirect(f'{template_base}s')
                return render(request, f'traffic/create_{template_base}.html', {
                    'form': form,
                    template_base: obj,
                    'error': 'Форма была неверной',
                })
            else:
                form = form_class(instance=obj)
                return render(request, f'traffic/create_{template_base}.html', {
                    'form': form,
                    template_base: obj,
                })

        if pk is not None:
            obj = get_object_or_404(model, pk=pk)
            if model == Traffic:
                obj = get_object_or_404(Traffic.objects.select_related('road_segment', 'congestion_type'), pk=pk)
            elif model == RoadSegment:
                obj = get_object_or_404(RoadSegment.objects.select_related('point_a', 'point_b', 'traffic__congestion_type'), pk=pk)
            return render(request, f'traffic/detail_{template_base}.html', {template_base: obj})

        queryset = model.objects.all()
        if model == RoadSegment:
            queryset = queryset.select_related('point_a', 'point_b')
        elif model == Traffic:
            queryset = queryset.select_related('road_segment', 'congestion_type')
        elif model == Location:
            queryset = queryset.order_by('name')
        return render(request, f'traffic/list_{template_base}s.html', {f'{template_base}s': queryset})

    return handler

location_handler = create_crud_handler(Location, LocationForm, 'location')
road_handler = create_crud_handler(RoadSegment, RoadSegmentForm, 'road', serialize_func=serialize_road_segment)
contype_handler = create_crud_handler(CongestionType, CongestionTypeForm, 'contype')
traffic_handler = create_crud_handler(Traffic, TrafficForm, 'traffic', serialize_func=serialize_traffic)

def home(request):
    return render(request, 'traffic/home.html')

def graph_api(request):
    locations = Location.objects.all().values('id', 'name', 'latitude', 'longitude')
    roads = RoadSegment.objects.select_related('point_a', 'point_b', 'traffic__congestion_type').all()
    edges = []
    for road in roads:
        coeff = road.traffic.congestion_type.time_coefficient if hasattr(road, 'traffic') else 1.0
        edges.append({
            'id': road.id,
            'from': road.point_a.id,
            'to': road.point_b.id,
            'distance_km': road.distance_km,
            'time_coefficient': coeff,
            'travel_time_minutes': road.distance_km * coeff
        })
    return JsonResponse({
        'locations': list(locations),
        'edges': edges,
    })

def api_locations(request):
    data = list(Location.objects.all().values('id', 'name', 'latitude', 'longitude'))
    return JsonResponse(data, safe=False)

def api_roads(request):
    roads = RoadSegment.objects.select_related('point_a', 'point_b', 'traffic__congestion_type').all()
    data = [serialize_road_segment(road) for road in roads]
    return JsonResponse(data, safe=False)

def api_contypes(request):
    data = list(CongestionType.objects.all().values('id', 'name', 'time_coefficient'))
    return JsonResponse(data, safe=False)

def api_traffic(request):
    traffics = Traffic.objects.select_related('road_segment', 'congestion_type').all()
    data = [serialize_traffic(t) for t in traffics]
    return JsonResponse(data, safe=False)

@csrf_exempt
def randomize_congestion_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        free = CongestionType.objects.get(name='Свободно')
        medium = CongestionType.objects.get(name='Затор')
        jam = CongestionType.objects.get(name='Пробка')
    except CongestionType.DoesNotExist as e:
        return JsonResponse({'error': str(e)}, status=500)

    prob_free = float(request.POST.get('prob_free', 0.6))
    prob_medium = float(request.POST.get('prob_medium', 0.3))
    prob_jam = float(request.POST.get('prob_jam', 0.1))
    weights = [prob_free, prob_medium, prob_jam]
    total = sum(weights)
    weights = [w / total for w in weights]

    types = [free, medium, jam]

    updated = 0
    for traffic in Traffic.objects.select_related('congestion_type'):
        new_type = random.choices(types, weights=weights)[0]
        if traffic.congestion_type != new_type:
            traffic.congestion_type = new_type
            traffic.save()
            updated += 1

    return JsonResponse({'status': 'ok', 'updated': updated})

@csrf_exempt
def set_all_free_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        free_type = CongestionType.objects.get(name='Свободно')
    except CongestionType.DoesNotExist:
        return JsonResponse({'error': 'Тип "Свободно" не найден'}, status=404)

    updated = Traffic.objects.update(congestion_type=free_type)
    return JsonResponse({'status': 'ok', 'updated': updated})

@csrf_exempt
def set_congestion_by_time_of_day(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    from datetime import datetime
    now = datetime.now().hour

    if 7 <= now < 10:
        probs = {'Свободно': 0.1, 'Затор': 0.3, 'Пробка': 0.6}
    elif 10 <= now < 17:
        probs = {'Свободно': 0.7, 'Затор': 0.2, 'Пробка': 0.1}
    elif 17 <= now < 20:
        probs = {'Свободно': 0.2, 'Затор': 0.3, 'Пробка': 0.5}
    else:
        probs = {'Свободно': 0.9, 'Затор': 0.1, 'Пробка': 0.0}

    types_map = {t.name: t for t in CongestionType.objects.all()}
    if not all(name in types_map for name in probs):
        return JsonResponse({'error': 'Не найдены нужные типы загруженности'}, status=500)

    updated = 0
    for traffic in Traffic.objects.select_related('congestion_type'):
        import random
        names = list(probs.keys())
        weights = list(probs.values())
        chosen_name = random.choices(names, weights=weights)[0]
        new_type = types_map[chosen_name]
        if traffic.congestion_type != new_type:
            traffic.congestion_type = new_type
            traffic.save()
            updated += 1

    return JsonResponse({'status': 'ok', 'updated': updated, 'period': now})

def get_edges_for_point(request, point_id):
    roads = RoadSegment.objects.filter(
        models.Q(point_a_id=point_id) | models.Q(point_b_id=point_id)
    ).select_related('point_a', 'point_b', 'traffic__congestion_type')
    data = [serialize_road_segment(road) for road in roads]
    return JsonResponse(data, safe=False)

def current_weights(request):
    data = {}
    for traffic in Traffic.objects.select_related('road_segment', 'congestion_type'):
        travel_time = traffic.road_segment.distance_km * traffic.congestion_type.time_coefficient
        data[traffic.road_segment.id] = travel_time
    return JsonResponse(data)

def weights_since(request):
    """
    Параметры: ?since=2025-05-12T15:30:00
    """
    since_str = request.GET.get('since')
    if not since_str:
        return current_weights(request)

    since = parse_datetime(since_str)
    if since is None:
        return JsonResponse({'error': 'Invalid datetime format. Use ISO format.'}, status=400)

    changed_traffic = Traffic.objects.filter(last_updated__gt=since).select_related('road_segment', 'congestion_type')
    data = {}
    for traffic in changed_traffic:
        travel_time = traffic.road_segment.distance_km * traffic.congestion_type.time_coefficient
        data[traffic.road_segment.id] = travel_time

    from django.utils import timezone
    server_time = timezone.now().isoformat()

    return JsonResponse({
        'changed': data,
        'server_time': server_time
    })