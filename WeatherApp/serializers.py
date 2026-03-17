from rest_framework import serializers


class WeatherLoadRequestSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()