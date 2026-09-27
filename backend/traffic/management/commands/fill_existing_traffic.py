from django.core.management.base import BaseCommand
from traffic.models import RoadSegment, Traffic, CongestionType


class Command(BaseCommand):
    help = 'Создаёт записи Traffic для всех RoadSegment, у которых их ещё нет'

    def handle(self, *args, **options):
        free_type, _ = CongestionType.objects.get_or_create(
            name='Свободно',
            defaults={'time_coefficient': 1.0}
        )
        roads_without_traffic = RoadSegment.objects.filter(traffic__isnull=True)
        count = roads_without_traffic.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('Все дороги уже имеют Traffic'))
            return

        created = 0
        for road in roads_without_traffic:
            Traffic.objects.create(road_segment=road, congestion_type=free_type)
            created += 1

        self.stdout.write(self.style.SUCCESS(f'Создано {created} записей Traffic'))