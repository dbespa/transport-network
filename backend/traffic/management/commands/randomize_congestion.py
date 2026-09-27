import random
from django.core.management.base import BaseCommand
from traffic.models import Traffic, CongestionType

class Command(BaseCommand):
    help = 'Присваивает каждому отрезку случайный тип загруженности'

    def add_arguments(self, parser):
        parser.add_argument(
            '--prob',
            nargs='+',
            type=float,
            default=[0.6, 0.3, 0.1],
            help='Вероятности для типов (Свободно, Затор, Пробка)'
        )

    def handle(self, *args, **options):
        probs = options['prob']
        if len(probs) != 3:
            self.stdout.write(self.style.ERROR('Недостаточно значений'))
            return

        try:
            free = CongestionType.objects.get(name='Свободно')
            medium = CongestionType.objects.get(name='Затор')
            jam = CongestionType.objects.get(name='Пробка')
        except CongestionType.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'Тип не найден: {e}'))
            return

        types = [free, medium, jam]
        total = sum(probs)
        weights = [p / total for p in probs]

        updated = 0
        for traffic in Traffic.objects.select_related('congestion_type'):
            new_type = random.choices(types, weights=weights)[0]
            if traffic.congestion_type != new_type:
                traffic.congestion_type = new_type
                traffic.save()
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Обновлено {updated} отрезков. Распределение: свободно ~{probs[0]*100}%, средне ~{probs[1]*100}%, пробка ~{probs[2]*100}%'
        ))