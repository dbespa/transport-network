import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from traffic.models import RoadSegment


class Command(BaseCommand):
    help = 'Экспортирует все отрезки дорог в CSV'

    def add_arguments(self, parser):
        parser.add_argument('--output', '-o', type=str, help='Имя выходного файла (по умолчанию roads_YYYY-MM-DD.csv)')

    def handle(self, *args, **options):
        if options['output']:
            filename = options['output']
        else:
            filename = f"roads_{datetime.now().strftime('%Y-%m-%d')}.csv"

        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['point_a_name', 'point_b_name', 'distance_km'])
            for road in RoadSegment.objects.select_related('point_a', 'point_b').all():
                writer.writerow([
                    road.point_a.name,
                    road.point_b.name,
                    road.distance_km
                ])
        self.stdout.write(self.style.SUCCESS(f'Экспортировано {RoadSegment.objects.count()} дорог в {filename}'))