import aiohttp
from django.conf import settings

from ..services import log_function_call_with_timing
from .base_client import BaseAsyncAPIClient


class NetatmoAPIClient(BaseAsyncAPIClient):
    def __init__(self):
        self.token = settings.NETATMO_TOKEN
        self.base_url = settings.NETATMO_BASE_URL
        self.source = "netatmo"

    def set_auth_token(self) -> None:
        self.add_headers({"Authorization": f"Bearer {self.token}"})

    def set_query_params(self, lat_ne: float, lon_ne: float, lat_sw: float, lon_sw: float) -> None:
        """
        example of query params dict:
            {"lat_ne": "45.49680784095829",
             "lon_ne": "9.219398119853263",
             "lat_sw": "45.49531886461733",
             "lon_sw": "9.216060089420624",
             }
        """
        self.add_query_params(
            {
                "lat_ne": float(lat_ne),
                "lon_ne": float(lon_ne),
                "lat_sw": float(lat_sw),
                "lon_sw": float(lon_sw),
                "filter": "false",
            }
        )

    @log_function_call_with_timing
    async def get_weather_data(self, endpoint="getpublicdata", **kwargs) -> dict:
        self.set_query_params(**kwargs)
        self.set_auth_token()
        url = f"{self.base_url}/{endpoint}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, params=self.query_params) as response:
                    response.raise_for_status()
                    return await response.text()
            except aiohttp.ClientError as e:
                print(f"An error occurred calling Netatmo API: {e}")
                raise aiohttp.ClientError({"Error": str(e)})
