from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Location(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    latitude = models.FloatField(verbose_name="Широта")
    longitude = models.FloatField(verbose_name="Долгота")

    class Meta:
        verbose_name = 'Населённый пункт'
        verbose_name_plural = 'Населённые пункты'
        unique_together = ('latitude', 'longitude')

    def __str__(self):
        return self.name

class RoadSegment(models.Model):
    point_a = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='road_segment_start', verbose_name="Точка А")
    point_b = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='road_segment_end', verbose_name="Точка B")
    distance_km = models.FloatField(verbose_name="Расстояние (км)")

    def travel_time_minutes(self):
        traffic = getattr(self, 'traffic', None)
        if traffic:
            coefficient = traffic.congestion_type.time_coefficient
        else:
            coefficient = 1.0

        base_speed_kmh = 60.0
        time_hours = self.distance_km / base_speed_kmh
        time_minutes = time_hours * 60
        return time_minutes * coefficient

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.point_a == self.point_b:
            raise ValidationError("Точка А и точка Б не могут совпадать")

    def save(self, *args, **kwargs):
        if self.point_a.id > self.point_b.id:
            self.point_a, self.point_b = self.point_b, self.point_a
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Отрезок пути'
        verbose_name_plural = 'Отрезки пути'
        unique_together = ('point_a', 'point_b')

    def __str__(self):
        return f"{self.point_a} -> {self.point_b} ({self.distance_km} км)"

class CongestionType(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название типа")
    time_coefficient = models.FloatField(default=1.0, verbose_name="Коэффициент времени")

    class Meta:
        verbose_name = 'Тип загруженности'
        verbose_name_plural = 'Типы загруженности'

    def __str__(self):
        return self.name

class Traffic(models.Model):
    road_segment = models.OneToOneField(
        RoadSegment,
        on_delete=models.CASCADE,
        related_name='traffic',
        verbose_name="Отрезок пути"
    )
    congestion_type = models.ForeignKey(CongestionType, on_delete=models.PROTECT, verbose_name="Тип загруженности")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    class Meta:
        verbose_name = 'Загруженность дороги'
        verbose_name_plural = 'Загруженность дорог'

    def __str__(self):
        return f"Загруженность на {self.road_segment}: {self.congestion_type.name}"

    def get_time_coefficient(self):
        return self.congestion_type.time_coefficient

@receiver(post_save, sender=RoadSegment)
def create_traffic_for_road(sender, instance, created, **kwargs):
    if created:
        free_type, _ = CongestionType.objects.get_or_create(
            name='Свободно',
            defaults={'time_coefficient': 1.0}
        )
        Traffic.objects.get_or_create(
            road_segment=instance,
            defaults={'congestion_type': free_type}
        )