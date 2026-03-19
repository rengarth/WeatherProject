import logging

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    WeatherClearResponseSerializer,
    TemperatureThresholdQuerySerializer,
    WeatherCountSerializer,
    WeatherDynamicFilterSerializer,
    WeatherLoadRequestSerializer,
    WeatherLoadResponseSerializer,
    WeatherRecordSerializer,
)
from .services import WeatherService

logger = logging.getLogger(__name__)


class WeatherLoadView(APIView):
    @extend_schema(
        request=WeatherLoadRequestSerializer,
        responses={200: WeatherLoadResponseSerializer},
        description='Loads weather data from Open-Meteo for the selected period and saves it to the database.'
    )
    def post(self, request):
        logger.info('POST /api/v1/weather/load/')
        serializer = WeatherLoadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = WeatherService()
        load_result = service.load_weather_data(
            latitude=serializer.validated_data['latitude'],
            longitude=serializer.validated_data['longitude'],
            start_date=serializer.validated_data['start_date'],
            end_date=serializer.validated_data['end_date'],
        )

        return Response(
            {
                'message': 'Weather data loaded successfully',
                'created_records_count': load_result['created_records_count'],
                'updated_records_count': load_result['updated_records_count'],
                'total_records_processed': load_result['total_records_processed'],
            },
            status=status.HTTP_200_OK
        )


class WeatherRecordListView(APIView):
    @extend_schema(
        responses={200: WeatherRecordSerializer(many=True)},
        description='Returns the full list of weather records stored in the database.'
    )
    def get(self, request):
        logger.info('GET /api/v1/weather/records/')
        service = WeatherService()
        serializer = WeatherRecordSerializer(service.get_all_records(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={200: WeatherClearResponseSerializer},
        description='Deletes all weather records from the database and returns the number of deleted rows.'
    )
    def delete(self, request):
        logger.info('DELETE /api/v1/weather/records/')
        service = WeatherService()
        deleted_records_count = service.clear_all_records()
        return Response(
            {
                'message': 'All weather records deleted successfully',
                'deleted_records_count': deleted_records_count,
            },
            status=status.HTTP_200_OK,
        )


class SunnyDaysListView(APIView):
    @extend_schema(
        responses={200: WeatherRecordSerializer(many=True)},
        description='Returns weather records for sunny days only (weather_code 0 and 1).'
    )
    def get(self, request):
        logger.info('GET /api/v1/weather/records/sunny/')
        service = WeatherService()
        serializer = WeatherRecordSerializer(service.get_sunny_days(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SunnyDaysCountView(APIView):
    @extend_schema(
        responses={200: WeatherCountSerializer},
        description='Returns the number of sunny days (weather_code 0 and 1).'
    )
    def get(self, request):
        logger.info('GET /api/v1/weather/records/sunny/count/')
        service = WeatherService()
        return Response(
            {'count': service.get_sunny_days_count()},
            status=status.HTTP_200_OK,
        )


class TemperatureAboveThresholdListView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='threshold',
                type=float,
                location=OpenApiParameter.QUERY,
                required=True,
                description='Returns all days where the maximum temperature is greater than the provided threshold.',
            ),
        ],
        responses={200: WeatherRecordSerializer(many=True)},
        description='Returns weather records where the maximum temperature is greater than a given value.'
    )
    def get(self, request):
        logger.info('GET /api/v1/weather/records/temperature-above/')
        query_serializer = TemperatureThresholdQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        service = WeatherService()
        serializer = WeatherRecordSerializer(
            service.get_days_above_temperature(query_serializer.validated_data['threshold']),
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TemperatureAboveThresholdCountView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='threshold',
                type=float,
                location=OpenApiParameter.QUERY,
                required=True,
                description='Counts all days where the maximum temperature is greater than the provided threshold.',
            ),
        ],
        responses={200: WeatherCountSerializer},
        description='Returns the number of days where the maximum temperature is greater than a given value.'
    )
    def get(self, request):
        logger.info('GET /api/v1/weather/records/temperature-above/count/')
        query_serializer = TemperatureThresholdQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        service = WeatherService()
        return Response(
            {'count': service.get_days_above_temperature_count(query_serializer.validated_data['threshold'])},
            status=status.HTTP_200_OK,
        )


class TopExtremeDaysView(APIView):
    @extend_schema(
        responses={200: WeatherRecordSerializer(many=True)},
        description='Returns the top 3 days sorted by highest maximum temperature and then by strongest wind.'
    )
    def get(self, request):
        logger.info('GET /api/v1/weather/records/top-extreme/')
        service = WeatherService()
        serializer = WeatherRecordSerializer(
            service.get_top_3_hottest_and_windiest_days(),
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class WeatherFilterView(APIView):
    @extend_schema(
        request=WeatherDynamicFilterSerializer,
        responses={200: WeatherRecordSerializer(many=True)},
        description='Returns weather records filtered by dynamic criteria such as date range, temperatures, wind speed and weather codes.'
    )
    def post(self, request):
        logger.info('POST /api/v1/weather/records/filter/')
        serializer = WeatherDynamicFilterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = WeatherService()
        response_serializer = WeatherRecordSerializer(
            service.filter_records(serializer.validated_data),
            many=True,
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)
