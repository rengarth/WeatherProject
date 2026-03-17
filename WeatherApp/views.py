from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import WeatherLoadRequestSerializer
from .services import WeatherService


class WeatherLoadView(APIView):
    @extend_schema(
        request=WeatherLoadRequestSerializer,
        responses={200: None},
        description='Loads weather data from Open-Meteo for the selected period and saves it to the database.'
    )
    def post(self, request):
        serializer = WeatherLoadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = WeatherService()
        records_count = service.load_weather_data(
            latitude=serializer.validated_data['latitude'],
            longitude=serializer.validated_data['longitude'],
            start_date=serializer.validated_data['start_date'],
            end_date=serializer.validated_data['end_date'],
        )

        return Response(
            {
                'message': 'Weather data loaded successfully',
                'records_count': records_count,
            },
            status=status.HTTP_200_OK
        )