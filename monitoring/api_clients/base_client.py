from typing import Protocol


class BaseAsyncAPIClient(Protocol):
    def __init__(self, base_url: str) -> None: ...

    _headers: dict = {}
    _query_params: dict = {}
    source: str = ""

    @property
    def headers(self) -> dict:
        return self._headers

    def add_headers(self, headers: dict) -> None:
        self._headers.update(headers)

    @property
    def query_params(self) -> dict:
        return self._query_params

    def add_query_params(self, query_params: dict) -> None:
        self._query_params.update(query_params)

    async def get_weather_data(self, **kwargs) -> dict: ...
