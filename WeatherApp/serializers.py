from rest_framework import serializers

from .models import WeatherRecord


class WeatherLoadRequestSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, attrs):
        if attrs['start_date'] > attrs['end_date']:
            raise serializers.ValidationError('start_date must be less than or equal to end_date.')
        return attrs


class WeatherLoadResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    created_records_count = serializers.IntegerField()
    updated_records_count = serializers.IntegerField()
    total_records_processed = serializers.IntegerField()


class WeatherRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherRecord
        fields = [
            'date',
            'latitude',
            'longitude',
            'temperature_max',
            'temperature_min',
            'apparent_temperature_max',
            'apparent_temperature_min',
            'weather_code',
            'wind_speed_max',
        ]


class WeatherCountSerializer(serializers.Serializer):
    count = serializers.IntegerField()


class WeatherClearResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    deleted_records_count = serializers.IntegerField()


class WeatherFilterResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    records = WeatherRecordSerializer(many=True)


class TemperatureThresholdQuerySerializer(serializers.Serializer):
    threshold = serializers.FloatField()


class WeatherDynamicFilterSerializer(serializers.Serializer):
    ORDERING_CHOICES = [
        'date',
        '-date',
        'temperature_max',
        '-temperature_max',
        'temperature_min',
        '-temperature_min',
        'apparent_temperature_max',
        '-apparent_temperature_max',
        'apparent_temperature_min',
        '-apparent_temperature_min',
        'wind_speed_max',
        '-wind_speed_max',
    ]

    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    max_temperature_from = serializers.FloatField(required=False)
    max_temperature_to = serializers.FloatField(required=False)
    min_temperature_from = serializers.FloatField(required=False)
    min_temperature_to = serializers.FloatField(required=False)
    max_apparent_temperature_from = serializers.FloatField(required=False)
    max_apparent_temperature_to = serializers.FloatField(required=False)
    min_apparent_temperature_from = serializers.FloatField(required=False)
    min_apparent_temperature_to = serializers.FloatField(required=False)
    wind_speed_max_from = serializers.FloatField(required=False)
    wind_speed_max_to = serializers.FloatField(required=False)
    latitude_from = serializers.FloatField(required=False)
    latitude_to = serializers.FloatField(required=False)
    longitude_from = serializers.FloatField(required=False)
    longitude_to = serializers.FloatField(required=False)
    weather_codes = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=False,
    )
    ordering = serializers.ChoiceField(
        choices=ORDERING_CHOICES,
        required=False,
        default='-date',
    )

    def validate(self, attrs):
        if attrs.get('start_date') and attrs.get('end_date'):
            if attrs['start_date'] > attrs['end_date']:
                raise serializers.ValidationError('start_date must be less than or equal to end_date.')

        range_pairs = [
            ('max_temperature_from', 'max_temperature_to'),
            ('min_temperature_from', 'min_temperature_to'),
            ('max_apparent_temperature_from', 'max_apparent_temperature_to'),
            ('min_apparent_temperature_from', 'min_apparent_temperature_to'),
            ('wind_speed_max_from', 'wind_speed_max_to'),
            ('latitude_from', 'latitude_to'),
            ('longitude_from', 'longitude_to'),
        ]

        for min_field, max_field in range_pairs:
            min_value = attrs.get(min_field)
            max_value = attrs.get(max_field)
            if min_value is not None and max_value is not None and min_value > max_value:
                raise serializers.ValidationError(
                    f'{min_field} must be less than or equal to {max_field}.'
                )

        return attrs
