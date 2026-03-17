from datetime import date

from .clients import OpenMeteoClient
from .models import WeatherRecord


class WeatherService:
    def __init__(self):
        self.client = OpenMeteoClient()

    def load_weather_data(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date
    ) -> int:
        raw_data = self.client.get_weather_data(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
        )

        daily_data = raw_data.get('daily', {})

        dates = daily_data.get('time', [])
        temp_max_values = daily_data.get('temperature_2m_max', [])
        temp_min_values = daily_data.get('temperature_2m_min', [])
        apparent_temp_max_values = daily_data.get('apparent_temperature_max', [])
        apparent_temp_min_values = daily_data.get('apparent_temperature_min', [])
        weather_codes = daily_data.get('weather_code', [])
        wind_speed_max_values = daily_data.get('wind_speed_10m_max', [])

        records_count = 0

        for index in range(len(dates)):
            record_date = date.fromisoformat(dates[index])

            WeatherRecord.objects.update_or_create(
                date=record_date,
                defaults={
                    'temperature_max': temp_max_values[index],
                    'temperature_min': temp_min_values[index],
                    'apparent_temperature_max': apparent_temp_max_values[index],
                    'apparent_temperature_min': apparent_temp_min_values[index],
                    'weather_code': weather_codes[index],
                    'wind_speed_max': wind_speed_max_values[index],
                }
            )
            records_count += 1

        return records_count