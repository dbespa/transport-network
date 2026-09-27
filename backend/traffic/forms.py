from django.forms import ModelForm, TextInput, FloatField, NumberInput, DateTimeInput
from django import forms

from traffic.models import Location, RoadSegment, CongestionType, Traffic


class LocationForm(ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'latitude', 'longitude']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Название пункта'}),
            'latitude': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Широта'}),
            'longitude': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Долгота'}),
        }

class RoadSegmentForm(ModelForm):
    class Meta:
        model = RoadSegment
        fields = '__all__'

        widgets = {
            'point_a': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Точка А'}),
            'point_b': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Точка B'}),
            'distance_km': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Расстояние в км'})
        }

class CongestionTypeForm(ModelForm):
    class Meta:
        model = CongestionType
        fields = ['name', 'time_coefficient']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Название'}),
            'time_coefficient': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Коэффициент времени'}),
        }

class TrafficForm(ModelForm):
    class Meta:
        model = Traffic
        fields = '__all__'
        exclude = ['last_updated']

        widgets = {
            'road_segment': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Дорога'}),
            'congestion_type': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Тип загруженности'}),
        }

