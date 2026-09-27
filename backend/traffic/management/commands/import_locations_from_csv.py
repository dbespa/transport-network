import csv
from django.core.management.base import BaseCommand
from traffic.models import Location

class Command(BaseCommand):
    help = 'Импортирует точки из CSV (поля: name, latitude, longitude)'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Путь к CSV файлу')

    def handle(self, *args, **options):
        with open(options['csv_file'], 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            created = 0
            for row in reader:
                obj, created_flag = Location.objects.get_or_create(
                    name=row['name'],
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude'])
                )
                if created_flag:
                    created += 1
            self.stdout.write(self.style.SUCCESS(f'Импортировано {created} новых точек'))