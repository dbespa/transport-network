import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from traffic.models import Location

class Command(BaseCommand):
    help = 'Экспортирует все точки в CSV (авто-имя)'

    def add_arguments(self, parser):
        parser.add_argument('--output', '-o', type=str, help='Имя выходного файла (по умолчанию locations_YYYY-MM-DD.csv)')

    def handle(self, *args, **options):
        if options['output']:
            filename = options['output']
        else:
            filename = f"locations_{datetime.now().strftime('%Y-%m-%d')}.csv"
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'latitude', 'longitude'])
            for loc in Location.objects.all():
                writer.writerow([loc.name, loc.latitude, loc.longitude])
        self.stdout.write(self.style.SUCCESS(f'Экспортировано в {filename}'))