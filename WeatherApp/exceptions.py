"""Пользовательские исключения предметной области погодного сервиса."""


class WeatherAppError(Exception):
    """Базовое исключение приложения с HTTP-статусом и кодом ошибки.

    Нужен как общий контракт для всех доменных ошибок, чтобы глобальный
    exception handler мог одинаково обрабатывать их и строить JSON-ответы.
    """

    status_code = 500
    default_detail = 'An internal server error occurred.'
    default_code = 'internal_server_error'

    def __init__(self, detail: str | None = None, code: str | None = None):
        """Инициализирует исключение сообщением и машинным кодом ошибки.

        Нужен, чтобы можно было при необходимости переопределить стандартный
        текст и код ошибки для конкретной ситуации.

        Args:
            detail (str | None): Человекочитаемое сообщение об ошибке.
            code (str | None): Машинный код ошибки для JSON-ответа.

        Returns:
            None: Метод только инициализирует объект исключения.
        """

        self.detail = detail or self.default_detail
        self.code = code or self.default_code
        super().__init__(self.detail)


class ExternalApiError(WeatherAppError):
    """Ошибка обращения к внешнему погодному API.

    Нужна для отделения проблем сети и внешнего сервиса от внутренних ошибок
    приложения и возврата клиенту корректного статуса 502.
    """

    status_code = 502
    default_detail = 'Failed to fetch data from the external weather API.'
    default_code = 'external_api_error'


class WeatherDataValidationError(WeatherAppError):
    """Ошибка валидации данных, пришедших от Open-Meteo.

    Нужна, когда внешний сервис ответил формально успешно, но данные оказались
    неполными, битым JSON или не соответствуют ожидаемой структуре.
    """

    status_code = 502
    default_detail = 'The weather API returned invalid or incomplete data.'
    default_code = 'weather_data_validation_error'


class WeatherServiceError(WeatherAppError):
    """Ошибка бизнес-логики сервисного слоя.

    Нужна как обёртка над непредвиденными ошибками сервиса, чтобы не отдавать
    наружу внутренние детали реализации и при этом сохранить единый формат API.
    """

    status_code = 500
    default_detail = 'The weather service failed to process the request.'
    default_code = 'weather_service_error'
