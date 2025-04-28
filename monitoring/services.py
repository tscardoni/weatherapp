import asyncio
import json
import logging
import time

import psycopg2
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.timezone import now

from .models import PostgresStatusLog
from .serializers import NetatmoSerializer, OpenWeatherSerializer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_function_call_with_timing(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logging.info(
            f"{now()} - Calling function: {func.__name__} with arguments: {args} and keyword arguments: {kwargs}"
        )
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logging.info(f"Function: {func.__name__} returned: {result} (Execution time: {execution_time:.4f} seconds)")
        return result

    return wrapper


# Example: save the serializer synchronously but call it in an asynchronous context
@sync_to_async
def save_serializer(serializer):
    if serializer.is_valid():
        serializer.save()
        return True, "Success"
    else:
        return False, serializer.errors


async def fetch_and_save_weather(api_client, **kwargs):
    json_data = None  # Initialize json_data to avoid UnboundLocalError
    try:
        json_data = await api_client.get_weather_data(**kwargs)
    except Exception as e:
        if json_data and "403" in json_data:
            return {"error": f"Unauthorized {str(e)}"}
        elif json_data and "404" in json_data:
            return {"error": "No data found"}
        elif json_data and "500" in json_data:
            return {"error": "Internal server error"}
        else:
            return {"error": f"Unexpected error: {str(e)}"}
    # temporary debug print
    print(f"Data_type: {type(json_data)}")
    serializers = []
    if api_client.source == "openweather":
        serializers.append(OpenWeatherSerializer(data=json_data))
    elif api_client.source == "netatmo":
        for station in json.loads(json_data).get("body", []):
            serializers.append(NetatmoSerializer(data=station))
    else:
        raise ValueError("Invalid source")
    coros = []
    for serializer in serializers:
        coros.append(save_serializer(serializer))
    results = await asyncio.gather(*coros)
    success = all(result[0] for result in results)
    errors = [error for success, error in results if not success]
    count = len(results)

    if success:
        return {"message": f"N. {count} dati salvati con successo!"}
    else:
        return {"error": errors}


@log_function_call_with_timing
def check_postgres_status():
    try:
        conn = psycopg2.connect(
            dbname=settings.DATABASE_TO_MONITOR["default"]["NAME"],
            user=settings.DATABASE_TO_MONITOR["default"]["USER"],
            password=settings.DATABASE_TO_MONITOR["default"]["PASSWORD"],
            host=settings.DATABASE_TO_MONITOR["default"]["HOST"],
            port=settings.DATABASE_TO_MONITOR["default"]["PORT"],
        )
        conn.close()
        return True
    except Exception as e:
        print(f"Postgres Error: {e}")
        return False


@log_function_call_with_timing
def save_postgres_status():
    status = check_postgres_status()
    if status:
        return PostgresStatusLog.objects.create(status="up")
    else:
        return PostgresStatusLog.objects.create(status="down")
