"""ORM-модели погодного приложения."""

from django.db import models

from .querysets import WeatherRecordQuerySet


class WeatherRecord(models.Model):
    """Модель дневной погодной записи для конкретной даты и локации.

    Нужна для хранения погодных данных в Postgres и работы с ними через ORM,
    включая выборки, сортировки, фильтры и защиту от дублирования записей.
    """

    objects = WeatherRecordQuerySet.as_manager()

    date = models.DateField()
    latitude = models.FloatField()
    longitude = models.FloatField()
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
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'latitude', 'longitude'],
                name='unique_weather_record_per_date_and_location',
            ),
        ]

    def __str__(self):
        """Возвращает читаемое представление записи.

        Нужно для удобства отладки, логирования и просмотра объектов в shell
        или административных инструментах.

        Returns:
            str: Строковое представление погодной записи со значимыми полями.
        """

        return (f'{self.date} | '
                f'lat={self.latitude} | '
                f'lon={self.longitude} | '
                f'max={self.temperature_max} | '
                f'min={self.temperature_min} | '
                f'apparent={self.apparent_temperature_max} | '
                f'apparent={self.apparent_temperature_min} | '
                f'code={self.weather_code}  | '
                f'wind={self.wind_speed_max}')
