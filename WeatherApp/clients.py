"""Клиент для получения исторических погодных данных из Open-Meteo."""

import logging
from datetime import date
from pathlib import Path

import requests
import requests_cache
from retry_requests import retry

from .exceptions import ExternalApiError, WeatherDataValidationError

logger = logging.getLogger(__name__)


class OpenMeteoClient:
    """Инкапсулирует работу с Open-Meteo и скрывает детали HTTP-запросов.

    Нужен для того, чтобы слой сервиса не зависел от конкретной библиотеки
    запросов, настроек retry/cache и формата взаимодействия с внешним API.
    """

    BASE_URL = 'https://archive-api.open-meteo.com/v1/archive'
    CACHE_PATH = Path(__file__).resolve().parent.parent / '.cache' / 'openmeteo_cache'
    REQUEST_TIMEOUT_SECONDS = 30
    RETRIES = 5
    BACKOFF_FACTOR = 0.2

    def __init__(self):
        """Создаёт HTTP-сессию с кэшированием и повторными попытками.

        Это нужно, чтобы повторно не запрашивать одни и те же архивные данные
        и устойчивее переживать временные сетевые ошибки.

        Returns:
            None: Метод только инициализирует экземпляр клиента.
        """

        self.session = self._build_session()

    def get_weather_data(self, latitude: float, longitude: float, start_date: date, end_date: date) -> dict:
        """Получает погодные данные за диапазон дат для указанных координат.

        Нужен как единая точка входа в Open-Meteo: метод формирует параметры,
        делает запрос, проверяет корректность ответа и возвращает JSON дальше
        в сервисный слой.

        Args:
            latitude (float): Широта точки, для которой нужно получить погоду.
            longitude (float): Долгота точки, для которой нужно получить погоду.
            start_date (date): Начальная дата диапазона включительно.
            end_date (date): Конечная дата диапазона включительно.

        Returns:
            dict: JSON-словарь с погодными данными от Open-Meteo.

        Raises:
            ExternalApiError: Если HTTP-запрос завершился сетевой или серверной ошибкой.
            WeatherDataValidationError: Если ответ не содержит ожидаемую структуру
                или вернул невалидный JSON.
        """

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
            response = self.session.get(self.BASE_URL, params=params, timeout=self.REQUEST_TIMEOUT_SECONDS)
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

        logger.info(
            'Open-Meteo response received successfully: from_cache=%s',
            getattr(response, 'from_cache', False),
        )

        try:
            payload = response.json()
        except ValueError as exc:
            logger.error('Open-Meteo returned invalid JSON.', exc_info=(type(exc), exc, exc.__traceback__))
            raise WeatherDataValidationError(detail='The weather API returned invalid JSON.') from exc

        if 'daily' not in payload:
            logger.error('Open-Meteo response does not contain the "daily" section.')
            raise WeatherDataValidationError()

        return payload

    @classmethod
    def _build_session(cls):
        """Собирает session c файловым кэшем и механизмом retry.

        Нужен для централизации сетевых настроек клиента, чтобы не дублировать
        создание кэша и параметры повторных попыток в разных местах кода.

        Args:
            cls (type[OpenMeteoClient]): Класс клиента, из которого берутся настройки
                кэша, числа повторов и backoff.

        Returns:
            requests.Session: Подготовленная HTTP-сессия с кэшем и retry-механизмом.
        """

        cls.CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

        cache_session = requests_cache.CachedSession(
            cache_name=str(cls.CACHE_PATH),
            expire_after=-1,
        )
        return retry(
            cache_session,
            retries=cls.RETRIES,
            backoff_factor=cls.BACKOFF_FACTOR,
        )
