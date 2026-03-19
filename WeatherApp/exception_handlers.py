import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .exceptions import WeatherAppError

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
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
    view = context.get('view')
    return view.__class__.__name__ if view else 'unknown_view'


def _exception_info(exc: Exception):
    return type(exc), exc, exc.__traceback__
