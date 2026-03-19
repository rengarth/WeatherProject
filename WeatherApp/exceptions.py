class WeatherAppError(Exception):
    status_code = 500
    default_detail = 'An internal server error occurred.'
    default_code = 'internal_server_error'

    def __init__(self, detail: str | None = None, code: str | None = None):
        self.detail = detail or self.default_detail
        self.code = code or self.default_code
        super().__init__(self.detail)


class ExternalApiError(WeatherAppError):
    status_code = 502
    default_detail = 'Failed to fetch data from the external weather API.'
    default_code = 'external_api_error'


class WeatherDataValidationError(WeatherAppError):
    status_code = 502
    default_detail = 'The weather API returned invalid or incomplete data.'
    default_code = 'weather_data_validation_error'


class WeatherServiceError(WeatherAppError):
    status_code = 500
    default_detail = 'The weather service failed to process the request.'
    default_code = 'weather_service_error'
