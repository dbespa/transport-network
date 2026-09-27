import time
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from traffic.models import RoadSegment, Traffic, CongestionType

class Command(BaseCommand):
    help = 'Имитация загруженности по времени суток (утро, день, вечер, ночь)'

    def handle(self, *args, **options):
        free = CongestionType.objects.get(name='Свободно')
        medium = CongestionType.objects.get(name='Затор')
        jam = CongestionType.objects.get(name='Пробка')
        # closed = CongestionType.objects.get(name='Дорога перекрыта')

        self.stdout.write('Запуск имитации трафика по времени суток...')

        try:
            while True:
                now = timezone.now().hour
                if 7 <= now < 10:
                    period = 'morning'
                elif 10 <= now < 17:
                    period = 'day'
                elif 17 <= now < 20:
                    period = 'evening'
                else:
                    period = 'night'

                if period == 'morning':
                    types = [jam, medium]
                    probs = [0.7, 0.3]
                elif period == 'evening':
                    types = [jam, medium]
                    probs = [0.6, 0.4]
                elif period == 'day':
                    types = [free, medium]
                    probs = [0.8, 0.2]
                else:
                    types = [free, medium]
                    probs = [0.95, 0.05]

                roads = RoadSegment.objects.select_related('traffic').all()
                updated = 0
                for road in roads:
                    new_type = random.choices(types, weights=probs)[0]
                    if road.traffic.congestion_type != new_type:
                        road.traffic.congestion_type = new_type
                        road.traffic.save()
                        updated += 1

                self.stdout.write(f'{timezone.now().strftime("%H:%M")} - Период: {period}, обновлено {updated} дорог')

                time.sleep(60)

        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('Остановлено'))