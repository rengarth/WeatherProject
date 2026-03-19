"""Сервисный слой погодного приложения."""

import logging
from datetime import date

from .clients import OpenMeteoClient
from .exceptions import WeatherAppError, WeatherDataValidationError, WeatherServiceError
from .models import WeatherRecord

logger = logging.getLogger(__name__)


class WeatherService:
    """Инкапсулирует бизнес-логику загрузки, чтения и удаления погодных данных.

    Нужен для отделения предметных сценариев приложения от HTTP-слоя и деталей
    обращения к внешнему API или ORM.
    """

    def __init__(self, client: OpenMeteoClient | None = None):
        """Создаёт сервис и при необходимости принимает подменённый API-клиент.

        Нужен для удобства тестирования и сохранения слабой связности между
        сервисным слоем и конкретной реализацией внешнего клиента.

        Args:
            client (OpenMeteoClient | None): Подменённый клиент Open-Meteo, если
                нужно использовать не стандартную реализацию.

        Returns:
            None: Метод только инициализирует сервис.
        """

        self.client = client or OpenMeteoClient()

    def load_weather_data(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date
    ) -> dict:
        """Загружает погодные данные из Open-Meteo и сохраняет их в БД.

        Нужен как основной сценарий импорта: получает внешний ответ, валидирует
        его, делает upsert по дате и координатам и возвращает счётчики созданных
        и обновлённых записей.

        Args:
            latitude (float): Широта локации, для которой загружаются данные.
            longitude (float): Долгота локации, для которой загружаются данные.
            start_date (date): Начальная дата диапазона включительно.
            end_date (date): Конечная дата диапазона включительно.

        Returns:
            dict: Словарь со счётчиками созданных, обновлённых и обработанных записей.

        Raises:
            WeatherAppError: Если произошла ожидаемая доменная ошибка приложения.
            WeatherServiceError: Если произошла непредвиденная ошибка бизнес-логики.
        """

        logger.info(
            'Loading weather data into the database: latitude=%s longitude=%s start_date=%s end_date=%s',
            latitude,
            longitude,
            start_date,
            end_date,
        )

        try:
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

            self._validate_daily_series(
                dates=dates,
                temp_max_values=temp_max_values,
                temp_min_values=temp_min_values,
                apparent_temp_max_values=apparent_temp_max_values,
                apparent_temp_min_values=apparent_temp_min_values,
                weather_codes=weather_codes,
                wind_speed_max_values=wind_speed_max_values,
            )

            created_records_count = 0
            updated_records_count = 0

            for index in range(len(dates)):
                record_date = date.fromisoformat(dates[index])

                _, created = WeatherRecord.objects.update_or_create(
                    date=record_date,
                    latitude=latitude,
                    longitude=longitude,
                    defaults={
                        'temperature_max': temp_max_values[index],
                        'temperature_min': temp_min_values[index],
                        'apparent_temperature_max': apparent_temp_max_values[index],
                        'apparent_temperature_min': apparent_temp_min_values[index],
                        'weather_code': weather_codes[index],
                        'wind_speed_max': wind_speed_max_values[index],
                    },
                )
                if created:
                    created_records_count += 1
                else:
                    updated_records_count += 1

            total_records_processed = created_records_count + updated_records_count
            logger.info(
                'Weather data load completed successfully: created_records_count=%s updated_records_count=%s total_records_processed=%s',
                created_records_count,
                updated_records_count,
                total_records_processed,
            )
            return {
                'created_records_count': created_records_count,
                'updated_records_count': updated_records_count,
                'total_records_processed': total_records_processed,
            }
        except WeatherAppError:
            raise
        except Exception as exc:
            logger.exception(
                'Unexpected error while loading weather data',
                exc_info=(type(exc), exc, exc.__traceback__),
            )
            raise WeatherServiceError() from exc

    def get_all_records(self):
        """Возвращает все сохранённые погодные записи.

        Нужен для endpoint'а просмотра полного списка данных из базы.

        Returns:
            QuerySet[WeatherRecord]: Все погодные записи из базы данных.
        """

        logger.info('Fetching all weather records')
        return WeatherRecord.objects.all()

    def get_sunny_days(self):
        """Возвращает только солнечные дни.

        Нужен для отдельного сценария аналитики по кодам погоды 0 и 1.

        Returns:
            QuerySet[WeatherRecord]: Записи только по солнечным дням.
        """

        logger.info('Fetching sunny weather records')
        return WeatherRecord.objects.sunny()

    def get_sunny_days_count(self) -> int:
        """Считает количество солнечных дней.

        Нужен для endpoint'а, который возвращает только число солнечных дней
        без передачи полного списка записей.

        Returns:
            int: Количество солнечных дней в базе данных.
        """

        logger.info('Counting sunny weather records')
        return WeatherRecord.objects.sunny().count()

    def get_days_above_temperature(self, threshold: float):
        """Возвращает дни, где максимальная температура выше порога.

        Нужен для аналитики и пользовательского поиска по температурному
        условию.

        Args:
            threshold (float): Температурный порог для поля `temperature_max`.

        Returns:
            QuerySet[WeatherRecord]: Записи, где максимальная температура выше порога.
        """

        logger.info('Fetching weather records above threshold=%s', threshold)
        return WeatherRecord.objects.above_temperature(threshold)

    def get_days_above_temperature_count(self, threshold: float) -> int:
        """Считает дни, где максимальная температура выше порога.

        Нужен для сценария, когда клиенту требуется только итоговый счётчик,
        а не полный список записей.

        Args:
            threshold (float): Температурный порог для поля `temperature_max`.

        Returns:
            int: Количество дней, где максимальная температура выше порога.
        """

        logger.info('Counting weather records above threshold=%s', threshold)
        return WeatherRecord.objects.above_temperature(threshold).count()

    def get_top_3_hottest_and_windiest_days(self):
        """Возвращает топ-3 самых жарких и ветреных дней.

        Нужен для выполнения требования тестового задания по поиску трёх
        наиболее экстремальных дней.

        Returns:
            QuerySet[WeatherRecord]: Не более трёх записей, отсортированных по
                максимальной температуре и силе ветра.
        """

        logger.info('Fetching top 3 hottest and windiest weather records')
        return WeatherRecord.objects.hottest_and_windiest()[:3]

    def filter_records(self, filters: dict):
        """Возвращает записи, подходящие под динамический набор фильтров.

        Нужен для универсального endpoint'а поиска, где условия приходят от
        клиента и могут комбинироваться произвольным образом.

        Args:
            filters (dict): Словарь с динамическими критериями фильтрации.

        Returns:
            QuerySet[WeatherRecord]: Записи, удовлетворяющие переданным условиям.
        """

        logger.info('Filtering weather records with criteria=%s', filters)
        return WeatherRecord.objects.apply_filters(filters)

    def clear_all_records(self) -> int:
        """Удаляет все погодные записи из базы.

        Нужен для административного сценария очистки таблицы и возврата
        количества удалённых строк.

        Returns:
            int: Количество удалённых записей из таблицы погодных данных.
        """

        logger.info('Deleting all weather records from the database')
        deleted_count, _ = WeatherRecord.objects.all().delete()
        logger.info('Weather records deleted successfully: deleted_count=%s', deleted_count)
        return deleted_count

    @staticmethod
    def _validate_daily_series(**series):
        """Проверяет, что все массивы из ответа Open-Meteo одной длины.

        Нужен для защиты от неконсистентных данных внешнего API, чтобы не
        получить ошибки индексации и не сохранить повреждённые записи.

        Args:
            **series: Набор именованных массивов из ответа Open-Meteo, где ключ
                `dates` используется как эталон длины.

        Returns:
            None: Метод ничего не возвращает, а только валидирует входные данные.

        Raises:
            WeatherDataValidationError: Если длина хотя бы одного массива не совпадает
                с количеством дат.
        """

        dates = series.get('dates', [])
        expected_length = len(dates)

        for field_name, values in series.items():
            if len(values) != expected_length:
                raise WeatherDataValidationError(
                    detail=f'Invalid weather data: field "{field_name}" does not match the number of dates.'
                )
