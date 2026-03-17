from django.contrib import admin
from .models import WeatherRecord


@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'temperature_max',
        'temperature_min',
        'apparent_temperature_max',
        'apparent_temperature_min',
        'weather_code',
        'wind_speed_max',
        'created_at',
        'updated_at',
    )
    search_fields = ('date',)
    ordering = ('-date',)