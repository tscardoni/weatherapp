import json
from datetime import datetime
from pathlib import Path

import pytest
from asyncmock import AsyncMock


@pytest.fixture(autouse=True)
def reset_db_after_test(transactional_db):
    from django.db import connection

    yield
    connection.rollback()


def load_json(name):
    with open(Path(__file__).parent / "data" / f"{name}.json") as f:
        return json.load(f)


@pytest.fixture
def openweather_data():
    return load_json("openweather")


@pytest.fixture
def netatmo_data():
    return load_json("netatmo")


@pytest.fixture
def weather_station():
    return {
        "name": "Milan - Test Locality",
        "latitude": 45.0,
        "longitude": 9.0,
        "city": "Milan",
        "locality": "Test Locality",
        "source": "openweather",
        "source_id": "test_station_id",
    }


@pytest.fixture
def openweather_api_client():
    client_mock = AsyncMock()
    client_mock.get_weather_data = AsyncMock(return_value=load_json("openweather"))
    client_mock.source = "openweather"
    return client_mock
