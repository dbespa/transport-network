from django.core.management.base import BaseCommand
from django.utils import timezone
from traffic.models import RoadSegment, Traffic, CongestionType

class Command(BaseCommand):
    help = 'Устанавливает всем дорогам статус "Свободно", создавая записи Traffic при необходимости'

    def handle(self, *args, **options):
        free_type, _ = CongestionType.objects.get_or_create(
            name='Свободно',
            defaults={'time_coefficient': 1.0}
        )

        roads_without = RoadSegment.objects.filter(traffic__isnull=True)
        created = 0
        for road in roads_without:
            Traffic.objects.create(road_segment=road, congestion_type=free_type)
            created += 1
        if created:
            self.stdout.write(f'Создано {created} новых записей Traffic')

        updated = Traffic.objects.exclude(congestion_type=free_type).update(
            congestion_type=free_type,
            last_updated=timezone.now()
        )
        self.stdout.write(self.style.SUCCESS(f'Обновлено {updated} записей на тип "Свободно"'))