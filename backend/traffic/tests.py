from django.test import TestCase
from django.urls import reverse
from traffic.models import Location, RoadSegment, CongestionType, Traffic

class LocationModelTest(TestCase):
    def test_str_without_coordinates(self):
        loc = Location.objects.create(name='Тест', latitude=51.66, longitude=39.20)
        self.assertEqual(str(loc), 'Тест')

class RoadSegmentTest(TestCase):
    def setUp(self):
        self.a = Location.objects.create(name='A', latitude=0, longitude=0)
        self.b = Location.objects.create(name='B', latitude=1, longitude=1)
        free = CongestionType.objects.create(name='Свободно', time_coefficient=1.0)
        self.road = RoadSegment.objects.create(point_a=self.a, point_b=self.b, distance_km=10)
        Traffic.objects.create(road_segment=self.road, congestion_type=free)

    def test_travel_time_minutes(self):
        self.assertEqual(self.road.travel_time_minutes(), 10.0)

class CongestionTypeTest(TestCase):
    def test_time_coefficient(self):
        jam = CongestionType.objects.create(name='Пробка', time_coefficient=2.5)
        self.assertEqual(jam.time_coefficient, 2.5)

class APITest(TestCase):
    def setUp(self):
        CongestionType.objects.get_or_create(name='Свободно', defaults={'time_coefficient': 1.0})
        CongestionType.objects.get_or_create(name='Затор', defaults={'time_coefficient': 1.5})
        CongestionType.objects.get_or_create(name='Пробка', defaults={'time_coefficient': 2.5})
        self.loc = Location.objects.create(name='Воронеж', latitude=51.660, longitude=39.200)

    def test_graph_api_returns_valid_json(self):
        response = self.client.get(reverse('api_graph'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('locations', data)
        self.assertIn('edges', data)

    def test_randomize_congestion_api_only_post(self):
        response = self.client.get(reverse('api_randomize_congestion'))
        self.assertEqual(response.status_code, 405)  # GET запрещён

    def test_randomize_congestion_api_post_works(self):
        b = Location.objects.create(name='B', latitude=51.661, longitude=39.201)
        road = RoadSegment.objects.create(point_a=self.loc, point_b=b, distance_km=5)
        free = CongestionType.objects.get(name='Свободно')
        Traffic.objects.create(road_segment=road, congestion_type=free)
        response = self.client.post(reverse('api_randomize_congestion'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['updated'], 1)