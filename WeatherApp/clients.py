import logging
from datetime import date

import requests

from .exceptions import ExternalApiError, WeatherDataValidationError

logger = logging.getLogger(__name__)


class OpenMeteoClient:
    BASE_URL = 'https://archive-api.open-meteo.com/v1/archive'

    def get_weather_data(self, latitude: float, longitude: float, start_date: date, end_date: date) -> dict:
        logger.info(
            'Requesting weather data from Open-Meteo: latitude=%s longitude=%s start_date=%s end_date=%s',
            latitude,
            longitude,
            start_date,
            end_date,
        )

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

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error(
                'Open-Meteo request failed: latitude=%s longitude=%s start_date=%s end_date=%s',
                latitude,
                longitude,
                start_date,
                end_date,
                exc_info=(type(exc), exc, exc.__traceback__),
            )
            raise ExternalApiError() from exc

        try:
            payload = response.json()
        except ValueError as exc:
            logger.error('Open-Meteo returned invalid JSON.', exc_info=(type(exc), exc, exc.__traceback__))
            raise WeatherDataValidationError(detail='The weather API returned invalid JSON.') from exc

        if 'daily' not in payload:
            logger.error('Open-Meteo response does not contain the "daily" section.')
            raise WeatherDataValidationError()

        return payload
