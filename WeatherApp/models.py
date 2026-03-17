from django.db import models


class WeatherRecord(models.Model):
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
