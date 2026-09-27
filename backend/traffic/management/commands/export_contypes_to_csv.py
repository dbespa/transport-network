import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from traffic.models import CongestionType


class Command(BaseCommand):
    help = 'Экспортирует все типы загруженности в CSV (авто-имя)'

    def add_arguments(self, parser):
        parser.add_argument('--output', '-o', type=str,
                            help='Имя выходного файла (по умолчанию contypes_YYYY-MM-DD.csv)')

    def handle(self, *args, **options):
        if options['output']:
            filename = options['output']
        else:
            filename = f"contypes_{datetime.now().strftime('%Y-%m-%d')}.csv"

        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'time_coefficient'])
            for ct in CongestionType.objects.all():
                writer.writerow([
                    ct.name,
                    ct.time_coefficient
                ])
        self.stdout.write(self.style.SUCCESS(f'Экспортировано {CongestionType.objects.count()} типов в {filename}'))