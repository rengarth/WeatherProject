from django.urls import path
from .views import (
    SunnyDaysCountView,
    SunnyDaysListView,
    TemperatureAboveThresholdCountView,
    TemperatureAboveThresholdListView,
    TopExtremeDaysView,
    WeatherFilterView,
    WeatherLoadView,
    WeatherRecordListView,
)

urlpatterns = [
    path('load/', WeatherLoadView.as_view(), name='weather-load'),
    path('records/', WeatherRecordListView.as_view(), name='weather-record-list'),
    path('records/sunny/', SunnyDaysListView.as_view(), name='weather-sunny-list'),
    path('records/sunny/count/', SunnyDaysCountView.as_view(), name='weather-sunny-count'),
    path(
        'records/temperature-above/',
        TemperatureAboveThresholdListView.as_view(),
        name='weather-temperature-above-list',
    ),
    path(
        'records/temperature-above/count/',
        TemperatureAboveThresholdCountView.as_view(),
        name='weather-temperature-above-count',
    ),
    path('records/top-extreme/', TopExtremeDaysView.as_view(), name='weather-top-extreme'),
    path('records/filter/', WeatherFilterView.as_view(), name='weather-filter'),
]
