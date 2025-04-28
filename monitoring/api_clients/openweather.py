import aiohttp
from django.conf import settings

from ..services import log_function_call_with_timing
from .base_client import BaseAsyncAPIClient


class OpenWeatherAPIClient(BaseAsyncAPIClient):
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = settings.OPENWEATHER_BASE_URL
        self.source = "openweather"

    def set_query_params(self, lat: float, lon: float) -> None:
        """
        example of query params dict:
            {"lat": "45.49680784095829",
             "lon": "9.219398119853263",
             }
        """
        self.add_query_params(
            {
                "lat": float(lat),
                "lon": float(lon),
                "appid": self.api_key,
                "units": "metric",
                "lang": "en",
                "Mode": "json",
            }
        )

    @log_function_call_with_timing
    async def get_weather_data(self, endpoint="weather", **kwargs) -> dict:
        self.set_query_params(**kwargs)
        url = f"{self.base_url}/{endpoint}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=self.query_params) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                print(f"An error occurred calling OpenWeather API: {e}")
                return {"Error": str(e)}
