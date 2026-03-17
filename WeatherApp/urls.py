from django.urls import path
from .views import WeatherLoadView

urlpatterns = [
    path('load/', WeatherLoadView.as_view(), name='weather-load'),
]