import asyncio
from django.conf import settings

from .api_clients.netatmo import NetatmoAPIClient
from .api_clients.openweather import OpenWeatherAPIClient
from .services import fetch_and_save_weather, save_postgres_status

LAT = float(settings.LATITUDE)
LON = float(settings.LONGITUDE)
LAT_NE = float(settings.LATITUDE_NE)
LON_NE = float(settings.LONGITUDE_NE)
LAT_SW = float(settings.LATITUDE_SW)
LON_SW = float(settings.LONGITUDE_SW)


def fetch_weather_task(lat: float = LAT, lon: float = LON):
    """Launches data collection from OpenWeather"""
    api_client = OpenWeatherAPIClient()
    asyncio.run(fetch_and_save_weather(api_client, lat=lat, lon=lon))


def fetch_netatmo_weather_task(
    lat_ne: float = LAT_NE, lon_ne: float = LON_NE, lat_sw: float = LAT_SW, lon_sw: float = LON_SW
):
    """Launches data collection from Netatmo."""
    api_client = NetatmoAPIClient()
    asyncio.run(fetch_and_save_weather(api_client, lat_ne=lat_ne, lon_ne=lon_ne, lat_sw=lat_sw, lon_sw=lon_sw))


def check_postgres_task():
    """Launches the check for Postgres status"""
    save_postgres_status()
