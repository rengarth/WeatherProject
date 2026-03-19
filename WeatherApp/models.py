from django.db import models


class WeatherRecordQuerySet(models.QuerySet):
    def sunny(self):
        return self.filter(weather_code__in=[0, 1])

    def above_temperature(self, threshold: float):
        return self.filter(temperature_max__gt=threshold)

    def hottest_and_windiest(self):
        return self.order_by('-temperature_max', '-wind_speed_max', '-date')

    def apply_filters(self, filters: dict):
        queryset = self

        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        min_temperature_max = filters.get('min_temperature_max')
        max_temperature_max = filters.get('max_temperature_max')
        min_temperature_min = filters.get('min_temperature_min')
        max_temperature_min = filters.get('max_temperature_min')
        min_apparent_temperature_max = filters.get('min_apparent_temperature_max')
        max_apparent_temperature_max = filters.get('max_apparent_temperature_max')
        min_apparent_temperature_min = filters.get('min_apparent_temperature_min')
        max_apparent_temperature_min = filters.get('max_apparent_temperature_min')
        min_wind_speed_max = filters.get('min_wind_speed_max')
        max_wind_speed_max = filters.get('max_wind_speed_max')
        weather_codes = filters.get('weather_codes')

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if min_temperature_max is not None:
            queryset = queryset.filter(temperature_max__gte=min_temperature_max)
        if max_temperature_max is not None:
            queryset = queryset.filter(temperature_max__lte=max_temperature_max)
        if min_temperature_min is not None:
            queryset = queryset.filter(temperature_min__gte=min_temperature_min)
        if max_temperature_min is not None:
            queryset = queryset.filter(temperature_min__lte=max_temperature_min)
        if min_apparent_temperature_max is not None:
            queryset = queryset.filter(apparent_temperature_max__gte=min_apparent_temperature_max)
        if max_apparent_temperature_max is not None:
            queryset = queryset.filter(apparent_temperature_max__lte=max_apparent_temperature_max)
        if min_apparent_temperature_min is not None:
            queryset = queryset.filter(apparent_temperature_min__gte=min_apparent_temperature_min)
        if max_apparent_temperature_min is not None:
            queryset = queryset.filter(apparent_temperature_min__lte=max_apparent_temperature_min)
        if min_wind_speed_max is not None:
            queryset = queryset.filter(wind_speed_max__gte=min_wind_speed_max)
        if max_wind_speed_max is not None:
            queryset = queryset.filter(wind_speed_max__lte=max_wind_speed_max)
        if weather_codes:
            queryset = queryset.filter(weather_code__in=weather_codes)

        ordering = filters.get('ordering', '-date')
        return queryset.order_by(ordering)


class WeatherRecord(models.Model):
    objects = WeatherRecordQuerySet.as_manager()

    date = models.DateField(unique=True)
    temperature_max = models.FloatField()
    temperature_min = models.FloatField()
    apparent_temperature_max = models.FloatField()
    apparent_temperature_min = models.FloatField()
    weather_code = models.IntegerField()
    wind_speed_max = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'weather_records'
        ordering = ['-date']

    def __str__(self):
        return (f'{self.date} | '
                f'max={self.temperature_max} | '
                f'min={self.temperature_min} | '
                f'apparent={self.apparent_temperature_max} | '
                f'apparent={self.apparent_temperature_min} | '
                f'code={self.weather_code}  | '
                f'wind={self.wind_speed_max}')
