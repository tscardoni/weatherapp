import asyncio
from datetime import datetime
from unittest.mock import patch

import pytest
import pytest_asyncio
from asgiref.sync import sync_to_async
from django.test import AsyncClient
from django.urls import reverse
from django.utils import timezone

from monitoring.api_clients.openweather import OpenWeatherAPIClient
from monitoring.models import WeatherData, WeatherStation
from monitoring.serializers import (NetatmoSerializer, OpenWeatherSerializer,
                                    WeatherDataSerializer,
                                    WeatherStationSerializer)
from monitoring.services import fetch_and_save_weather


@sync_to_async
def get_weather_stations():
    return WeatherStation.objects.all()


@sync_to_async
def count_weather_stations(stations_obj):
    return stations_obj.count()


@sync_to_async
def first_weather_station(stations_obj):
    return stations_obj.first()


@sync_to_async
def stations_to_list(stations_obj):
    return list(stations_obj)


@sync_to_async
def get_weather_data():
    return WeatherData.objects.all()


@sync_to_async
def count_weather_data(data_obj):
    return data_obj.count()


@sync_to_async
def get_data_station(data_obj):
    return data_obj.station


@sync_to_async
def get_nth_obj(model_objs, n):
    return model_objs[n]


@sync_to_async
def first_weather_data(data_obj):
    return data_obj.first()


@sync_to_async
def list_weather_data(data_obj):
    return list(data_obj)


class TestWeatherStationSerializer:
    @pytest.mark.django_db
    def test_weather_station_serializer(self, weather_station):
        serializer = WeatherStationSerializer(data=weather_station)
        assert serializer.is_valid() is True
        my_station = serializer.save()
        assert my_station is not None
        assert my_station.name == "Milan - Test Locality"
        assert my_station.latitude == 45.0
        assert my_station.longitude == 9.0
        assert my_station.city == "Milan"
        assert my_station.locality == "Test Locality"
        assert my_station.source == "openweather"
        assert my_station.source_id == "test_station_id"

    @pytest.mark.django_db
    def test_weather_station_serializer_only_required(self):
        station_data = {
            "name": "Test Station",
            "source": "openweather",
            "source_id": "test_station_id",
        }
        serializer = WeatherStationSerializer(data=station_data)
        assert serializer.is_valid() is True
        my_station = serializer.save()

        assert my_station is not None

        assert my_station.name == "Test Station"
        assert my_station.source == "openweather"
        assert my_station.source_id == "test_station_id"


class TestWeatherDataSerializer:
    @pytest.mark.django_db
    def test_weather_data_serializer_with_station(self, weather_station):
        weather_data = {
            "temperature": 15.1,
            "feels_like": 14.1,
            "humidity": 93,
            "pressure": 1015,
            "timestamp": "2021-07-26T12:00:00",
        }
        station = WeatherStation.objects.create(**weather_station)
        assert station is not None
        assert WeatherStation.objects.count() == 1
        weather_data["station"] = station.id
        serializer = WeatherDataSerializer(data=weather_data)
        assert serializer.is_valid(), serializer.errors
        my_weather_data = serializer.save()
        assert my_weather_data is not None
        assert my_weather_data.station == station
        assert my_weather_data.temperature == 15.1
        assert my_weather_data.feels_like == 14.1
        assert my_weather_data.humidity == 93
        assert my_weather_data.pressure == 1015
        assert my_weather_data.timestamp == datetime(2021, 7, 26, 12, 0, tzinfo=timezone.get_current_timezone())


class TestOpenWeatherSerializer:
    @pytest.mark.django_db
    def test_openweather_serializer_only_required(self):
        json_data = {
            "main": {"temp": 15.1, "feels_like": 14.1, "humidity": 93, "pressure": 1015},
            "dt": 1627311600,
            "name": "Milan - Test Locality",
            "id": "test_station_id",
        }
        serializer = OpenWeatherSerializer(data=json_data)
        assert serializer.is_valid(), serializer.errors
        my_weather_data = serializer.save()
        assert my_weather_data is not None
        assert my_weather_data.station is not None
        assert my_weather_data.station.name == "Milan - Test Locality"
        assert my_weather_data.station.city is None
        assert my_weather_data.station.source_id == "test_station_id"
        assert my_weather_data.temperature == 15.1
        assert my_weather_data.feels_like == 14.1
        assert my_weather_data.humidity == 93
        assert my_weather_data.pressure == 1015
        assert my_weather_data.timestamp == timezone.make_aware(datetime.fromtimestamp(1627311600), timezone.get_current_timezone())

    @pytest.mark.django_db
    def test_openweather_serializer_all_fields(self, openweather_data):
        serializer = OpenWeatherSerializer(data=openweather_data)
        assert serializer.is_valid(), serializer.errors
        my_weather_data = serializer.save()
        assert my_weather_data is not None
        assert my_weather_data.station is not None
        assert my_weather_data.station.name == openweather_data["name"]
        assert my_weather_data.station.city is None
        assert my_weather_data.station.source_id == str(openweather_data["id"])
        assert my_weather_data.station.latitude == openweather_data["coord"]["lat"]
        assert my_weather_data.station.longitude == openweather_data["coord"]["lon"]
        assert my_weather_data.temperature == openweather_data["main"]["temp"]
        assert my_weather_data.feels_like == openweather_data["main"]["feels_like"]
        assert my_weather_data.humidity == openweather_data["main"]["humidity"]
        assert my_weather_data.pressure == openweather_data["main"]["pressure"]
        assert my_weather_data.timestamp == timezone.make_aware(
            datetime.fromtimestamp(openweather_data["dt"]), timezone.get_current_timezone()
        )
        assert WeatherStation.objects.count() == 1

    @pytest.mark.django_db
    def test_openweather_serializer_station_already_present(self, openweather_data):
        station = WeatherStation.objects.create(
            name=openweather_data["name"],
            source_id=openweather_data["id"],
            source="openweather",
            longitude=openweather_data["coord"]["lon"],
            latitude=openweather_data["coord"]["lat"],
        )
        serializer = OpenWeatherSerializer(data=openweather_data)
        assert serializer.is_valid(), serializer.errors
        my_weather_data = serializer.save()
        assert my_weather_data is not None
        assert my_weather_data.station == station
        assert my_weather_data.temperature == openweather_data["main"]["temp"]
        assert my_weather_data.feels_like == openweather_data["main"]["feels_like"]
        assert my_weather_data.humidity == openweather_data["main"]["humidity"]
        assert my_weather_data.pressure == openweather_data["main"]["pressure"]
        assert my_weather_data.timestamp == timezone.make_aware(
            datetime.fromtimestamp(openweather_data["dt"]), timezone.get_current_timezone()
        )


class TestNetatmoSerializer:
    @pytest.mark.django_db
    def test_netatmo_serializer_only_required(self, weather_station):
        json_data = {
            "_id": "70:ee:50:71:30:ae",
            "place": {
                "location": [9.22794373449619, 45.4832984744368],
                "city": "Milan",
                "street": "Test Locality",
            },
            "measures": {
                "02:00:00:6b:97:be": {"res": {"1741362399": [18.3, 47]}, "type": ["temperature", "humidity"]},
            },
        }
        station = WeatherStation.objects.create(**weather_station)
        assert station is not None
        assert WeatherStation.objects.count() == 1
        serializer = NetatmoSerializer(data=json_data)
        assert serializer.is_valid(), serializer.errors
        my_weather_data = serializer.save()
        assert my_weather_data is not None
        assert my_weather_data.station.name == station.name
        assert my_weather_data.temperature == 18.3
        assert my_weather_data.humidity == 47
        assert my_weather_data.timestamp is not None


class TestFetchAndSaveWeather:
    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_fetch_and_save_weather_openweather(self, openweather_api_client):
        params = {"lat": 45.0, "lon": 9.0}
        api_client = openweather_api_client
        result = await fetch_and_save_weather(api_client, **params)
        print(result)
        assert result == {"message": "N. 1 dati salvati con successo!"}


class TestMonitorView:
    @pytest.mark.django_db
    @pytest.mark.asyncio
    @patch("monitoring.api_clients.openweather.OpenWeatherAPIClient.get_weather_data")
    async def test_monitor_view_openweather(self,  mock_get_weather_data, openweather_api_client):
        async_client = AsyncClient()
        # test POST request with openweather data
        form_post_data = {
            "lat": 45.4968,
            "lon": 9.21940,
            "openweather_submit": "Submit",
        }
        # Mock the API client to return the openweather data
        mock_get_weather_data.return_value = asyncio.Future()
        mock_get_weather_data.return_value.set_result({
            "coord": {"lon": 10.1234, "lat": 46.7890},
            "weather": [
                {"id": 801, "main": "Clear", "description": "clear sky", "icon": "01d"}
            ],
            "base": "stations",
            "main": {
                "temp": 12.3,
                "feels_like": 10.5,
                "temp_min": 11.0,
                "temp_max": 13.5,
                "pressure": 1012,
                "humidity": 80,
                "sea_level": 1012,
                "grnd_level": 1000
            },
            "visibility": 9000,
            "wind": {"speed": 3.5, "deg": 180},
            "clouds": {"all": 10},
            "dt": 1741599999,
            "sys": {
                "type": 2,
                "id": 20400,
                "country": "IT",
                "sunrise": 1741588000,
                "sunset": 1741630000
            },
            "timezone": 3600,
            "id": 6694000,
            "name": "RandomCity",
            "cod": 200
        })
         
        response = await async_client.post(reverse("monitor_view"), data=form_post_data)

        assert response.status_code == 200
        assert response.context["message"] == {"message": "N. 1 dati salvati con successo!"}

        stations = await get_weather_stations()
        count = await count_weather_stations(stations)
        list = await stations_to_list(stations)
        print(f"Station list: {list}")
        assert count == 1
        first_station = await first_weather_station(stations)
        assert first_station.name == "RandomCity"
        assert first_station.source_id == "6694000"
        assert first_station.source == "openweather"
        assert first_station.latitude == 46.789
        assert first_station.longitude == 10.1234
        my_weather_data = await get_weather_data()
        print(f"Weather data: {await list_weather_data(my_weather_data)}")
        count_data = await count_weather_data(my_weather_data)
        assert count_data == 1
        first_data = await first_weather_data(my_weather_data)
        assert first_data.temperature == 12.3
        assert first_data.feels_like == 10.5
        assert first_data.humidity == 80
        assert first_data.pressure == 1012.0
        assert first_data.timestamp == datetime(2025, 3, 10, 9, 46, 39, tzinfo=timezone.utc)
        data_station = await get_data_station(first_data)
        assert data_station.name == first_station.name
