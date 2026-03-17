import requests
from datetime import date


class OpenMeteoClient:
    BASE_URL = 'https://archive-api.open-meteo.com/v1/archive'

    def get_weather_data(self, latitude: float, longitude: float, start_date: date, end_date: date) -> dict:
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'daily': [
                'temperature_2m_max',
                'temperature_2m_min',
                'apparent_temperature_max',
                'apparent_temperature_min',
                'weather_code',
                'wind_speed_10m_max',
            ],
            'wind_speed_unit': 'ms',
            'timezone': 'auto',
        }

        response = requests.get(self.BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()