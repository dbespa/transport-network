import csv
from django.core.management.base import BaseCommand
from traffic.models import RoadSegment, Location

class Command(BaseCommand):
    help = 'Импорт дорог из CSV. Точки сортируются, чтобы избежать дублей (A,B) и (B,A).'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        with open(options['csv_file'], 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            created = 0
            for row in reader:
                name_a = row['point_a_name']
                name_b = row['point_b_name']
                if name_a == name_b:
                    self.stdout.write(self.style.WARNING(f'Пропущена дорога из точки в себя: {name_a}'))
                    continue
                try:
                    point_a = Location.objects.get(name=name_a)
                    point_b = Location.objects.get(name=name_b)
                except Location.DoesNotExist as e:
                    self.stdout.write(self.style.WARNING(f'Точка не найдена: {e}'))
                    continue

                if point_a.id > point_b.id:
                    point_a, point_b = point_b, point_a

                distance = float(row['distance_km'])
                obj, created_flag = RoadSegment.objects.update_or_create(
                    point_a=point_a,
                    point_b=point_b,
                    defaults={'distance_km': distance}
                )
                if created_flag:
                    created += 1
            self.stdout.write(self.style.SUCCESS(f'Создано/обновлено {created} отрезков'))