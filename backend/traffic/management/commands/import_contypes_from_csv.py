import csv
from django.core.management.base import BaseCommand
from traffic.models import CongestionType

class Command(BaseCommand):
    help = 'Импортирует типы загруженности из CSV (поля: name, time_coefficient)'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        with open(options['csv_file'], 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['name']
                coeff = float(row['time_coefficient'])
                obj, created = CongestionType.objects.update_or_create(
                    name=name,
                    defaults={'time_coefficient': coeff}
                )
                if created:
                    self.stdout.write(f'Создан {name}')
                else:
                    self.stdout.write(f'Обновлён {name}')