"""Глобальная обработка ошибок DRF и приведение их к единому JSON-формату."""

import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .exceptions import WeatherAppError

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """Преобразует исключения приложения и DRF в единый JSON-ответ.

    Нужен для того, чтобы API возвращал предсказуемую структуру ошибок,
    удобную для клиентов, Swagger и логирования, вместо сырых traceback или
    разноформатных стандартных ответов.

    Args:
        exc (Exception): Исключение, которое нужно обработать.
        context (dict): Контекст DRF с информацией о текущем запросе и view.

    Returns:
        Response: HTTP-ответ DRF с унифицированным телом ошибки.
    """

    response = exception_handler(exc, context)

    if isinstance(exc, WeatherAppError):
        logger.error(
            'Handled weather application error in %s: %s',
            _get_view_name(context),
            exc.detail,
            exc_info=_exception_info(exc),
        )
        return Response(
            {
                'error': {
                    'code': exc.code,
                    'message': exc.detail,
                }
            },
            status=exc.status_code,
        )

    if response is not None:
        logger.warning(
            'Handled DRF exception in %s: status=%s',
            _get_view_name(context),
            response.status_code,
            exc_info=_exception_info(exc),
        )
        response.data = _build_error_payload(response.status_code, response.data, exc)
        return response

    logger.exception('Unhandled exception in %s', _get_view_name(context), exc_info=_exception_info(exc))
    return Response(
        {
            'error': {
                'code': 'internal_server_error',
                'message': 'An unexpected internal error occurred.',
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _build_error_payload(status_code: int, data, exc):
    """Собирает унифицированное тело ошибки для стандартных исключений DRF.

    Нужен для того, чтобы ответы об ошибках валидации и прочих HTTP-ошибках
    выглядели одинаково и их было проще обрабатывать на клиенте.

    Args:
        status_code (int): HTTP-статус ответа.
        data (object): Исходные данные ошибки, пришедшие от DRF.
        exc (Exception): Исключение, на основе которого строится ответ.

    Returns:
        dict: Словарь в едином формате ошибки API.
    """

    if isinstance(data, dict) and 'detail' in data:
        return {
            'error': {
                'code': getattr(exc, 'default_code', 'request_error'),
                'message': str(data['detail']),
            }
        }

    if isinstance(data, (dict, list)):
        return {
            'error': {
                'code': 'validation_error',
                'message': 'Request validation failed.',
                'details': data,
            }
        }

    return {
        'error': {
            'code': f'http_{status_code}_error',
            'message': str(data),
        }
    }


def _get_view_name(context: dict) -> str:
    """Возвращает имя view, в котором произошло исключение.

    Нужен для более информативного логирования: по имени view проще понять,
    на каком endpoint возникла проблема.

    Args:
        context (dict): Контекст DRF, потенциально содержащий объект view.

    Returns:
        str: Имя класса представления или строка `unknown_view`, если view отсутствует.
    """

    view = context.get('view')
    return view.__class__.__name__ if view else 'unknown_view'


def _exception_info(exc: Exception):
    """Подготавливает кортеж с информацией об исключении для логгера.

    Нужен, чтобы передавать в logging корректный traceback и получать
    подробные записи об ошибках в логах приложения.

    Args:
        exc (Exception): Исключение, по которому нужно собрать traceback.

    Returns:
        tuple[type[Exception], Exception, object]: Кортеж в формате, ожидаемом
            параметром `exc_info` в logging.
    """

    return type(exc), exc, exc.__traceback__
