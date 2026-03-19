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
        max_temperature_from = filters.get('max_temperature_from')
        max_temperature_to = filters.get('max_temperature_to')
        min_temperature_from = filters.get('min_temperature_from')
        min_temperature_to = filters.get('min_temperature_to')
        max_apparent_temperature_from = filters.get('max_apparent_temperature_from')
        max_apparent_temperature_to = filters.get('max_apparent_temperature_to')
        min_apparent_temperature_from = filters.get('min_apparent_temperature_from')
        min_apparent_temperature_to = filters.get('min_apparent_temperature_to')
        wind_speed_max_from = filters.get('wind_speed_max_from')
        wind_speed_max_to = filters.get('wind_speed_max_to')
        latitude_from = filters.get('latitude_from')
        latitude_to = filters.get('latitude_to')
        longitude_from = filters.get('longitude_from')
        longitude_to = filters.get('longitude_to')
        weather_codes = filters.get('weather_codes')

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if max_temperature_from is not None:
            queryset = queryset.filter(temperature_max__gte=max_temperature_from)
        if max_temperature_to is not None:
            queryset = queryset.filter(temperature_max__lte=max_temperature_to)
        if min_temperature_from is not None:
            queryset = queryset.filter(temperature_min__gte=min_temperature_from)
        if min_temperature_to is not None:
            queryset = queryset.filter(temperature_min__lte=min_temperature_to)
        if max_apparent_temperature_from is not None:
            queryset = queryset.filter(apparent_temperature_max__gte=max_apparent_temperature_from)
        if max_apparent_temperature_to is not None:
            queryset = queryset.filter(apparent_temperature_max__lte=max_apparent_temperature_to)
        if min_apparent_temperature_from is not None:
            queryset = queryset.filter(apparent_temperature_min__gte=min_apparent_temperature_from)
        if min_apparent_temperature_to is not None:
            queryset = queryset.filter(apparent_temperature_min__lte=min_apparent_temperature_to)
        if wind_speed_max_from is not None:
            queryset = queryset.filter(wind_speed_max__gte=wind_speed_max_from)
        if wind_speed_max_to is not None:
            queryset = queryset.filter(wind_speed_max__lte=wind_speed_max_to)
        if latitude_from is not None:
            queryset = queryset.filter(latitude__gte=latitude_from)
        if latitude_to is not None:
            queryset = queryset.filter(latitude__lte=latitude_to)
        if longitude_from is not None:
            queryset = queryset.filter(longitude__gte=longitude_from)
        if longitude_to is not None:
            queryset = queryset.filter(longitude__lte=longitude_to)
        if weather_codes:
            queryset = queryset.filter(weather_code__in=weather_codes)

        ordering = filters.get('ordering', '-date')
        return queryset.order_by(ordering)
