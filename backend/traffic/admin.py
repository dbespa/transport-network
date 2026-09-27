from django.contrib import admin
from django.utils.html import format_html
from .models import Location, RoadSegment, CongestionType, Traffic


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'latitude', 'longitude')
    search_fields = ('name',)


@admin.register(RoadSegment)
class RoadSegmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'point_a', 'point_b', 'distance_km')
    list_filter = ('point_a', 'point_b')


@admin.register(CongestionType)
class CongestionTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'time_coefficient')

    def color_display(self, obj):
        return format_html(
            '<div style="width: 30px; height: 20px; background-color: {}; border: 1px solid #000;"></div>',
            obj.color
        )

    color_display.short_description = 'Цвет'


@admin.register(Traffic)
class TrafficAdmin(admin.ModelAdmin):
    list_display = ('id', 'road_segment', 'congestion_type', 'last_updated', 'color_display')
    list_filter = ('congestion_type', 'last_updated')
    readonly_fields = ('last_updated',)

    def color_display(self, obj):
        color = obj.get_color()
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #000;"></div>',
            color
        )

    color_display.short_description = 'Цвет'