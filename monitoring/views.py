import json

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.timezone import now, timedelta
from django_q.models import Failure, Success

from .api_clients.netatmo import NetatmoAPIClient
from .api_clients.openweather import OpenWeatherAPIClient
from .forms import NetatmoForm, OpenWeatherForm
from .models import PostgresStatusLog, WeatherData, WeatherStation
from .serializers import NetatmoSerializer, OpenWeatherSerializer
from .services import check_postgres_status, fetch_and_save_weather

# Define the available intervals
INTERVALS = {
    "1h": timedelta(hours=1),
    "4h": timedelta(hours=4),
    "8h": timedelta(hours=8),
    "12h": timedelta(hours=12),
    "24h": timedelta(hours=24),
}


# Asynchronous view (requires Django 4.2+ and ASGI server)
async def monitor_view(request):
    open_form = OpenWeatherForm()
    netatmo_form = NetatmoForm()
    result = None

    if request.method == "POST":
        if "openweather_submit" in request.POST:
            open_form = OpenWeatherForm(request.POST)
            if open_form.is_valid():
                lat = open_form.cleaned_data["lat"]
                lon = open_form.cleaned_data["lon"]
                params = {"lat": lat, "lon": lon}
                client = OpenWeatherAPIClient()

        elif "netatmo_submit" in request.POST:
            netatmo_form = NetatmoForm(request.POST)
            if netatmo_form.is_valid():
                ne_lat = netatmo_form.cleaned_data["ne_lat"]
                ne_lon = netatmo_form.cleaned_data["ne_lon"]
                sw_lat = netatmo_form.cleaned_data["sw_lat"]
                sw_lon = netatmo_form.cleaned_data["sw_lon"]
                params = {"lat_ne": ne_lat, "lon_ne": ne_lon, "lat_sw": sw_lat, "lon_sw": sw_lon}
                client = NetatmoAPIClient()

        result = await fetch_and_save_weather(client, **params)  # async method

    return render(
        request,
        "monitoring/index.html",
        {
            "open_form": open_form,
            "netatmo_form": netatmo_form,
            "message": result,
        },
    )


async def task_dashboard(request):
    """Main page with live task graph and panel"""
    return render(request, "monitoring/task_dashboard.html")


async def task_stats_partial(request):
    """HTMX view that returns only updated task data"""
    one_hour_ago = now() - timedelta(hours=1)
    success_count = await Success.objects.filter(stopped__gte=one_hour_ago).acount()
    failure_count = await Failure.objects.filter(started__gte=one_hour_ago).acount()

    return render(
        request,
        "monitoring/partials/task_stats_partial.html",
        {"success_count": success_count, "failure_count": failure_count},
    )


def temperature_dashboard(request):
    """Main page with live temperature graph and panel"""
    stations = WeatherStation.objects.all()
    return render(request, "monitoring/temperature_dashboard.html", {"stations": stations})


def temperature_data_partial(request):
    """Partial view called by HTMX to update temperature data"""
    station_id = request.GET.get("station_id")
    interval = request.GET.get("interval", "1")
    # Validate the chosen interval
    time_delta = INTERVALS.get(interval, timedelta(hours=1))
    start_time = now() - time_delta

    if station_id:
        station = WeatherStation.objects.get(id=station_id)
        data = WeatherData.objects.filter(station=station, timestamp__gte=start_time).order_by("timestamp")
        # Prepare JSON-ready data
        labels = [entry.timestamp.strftime("%H:%M") for entry in data]
        temperatures = [entry.temperature for entry in data]
        # Prepare context in JSON format
        context = {
            "station_name": station.name,
            "labels": json.dumps(labels),
            "temperatures": json.dumps(temperatures),
            "interval": interval,
        }

        return render(
            request,
            "monitoring/partials/temperature_data_partial.html",
            context,
        )

    return JsonResponse({"error": "No data available"})


# Main view (loads the complete page)
def postgres_status_page(request):
    status = "up" if check_postgres_status() else "down"
    return render(request, "monitoring/postgres_status.html", {"status": status})


# View for partial updates only
def postgres_status_view(request):
    status = "up" if check_postgres_status() else "down"
    return render(
        request,
        "monitoring/partials/postgres_status_partial.html",
        {"status": status},
    )


def postgres_dashboard(request):
    """PostgreSQL dashboard with time interval selection."""
    interval = request.GET.get("interval", "1h")
    time_range = INTERVALS.get(interval, timedelta(hours=1))
    # Filter logs within the selected time interval
    logs = PostgresStatusLog.objects.filter(timestamp__gte=now() - time_range).order_by("-timestamp")
    # Ensure labels and statuses are always valid lists
    labels = [log.timestamp.strftime("%H:%M") for log in logs[::-1]] if logs else ["No data"]
    statuses = [1 if log.status == "up" else 0 for log in logs[::-1]] if logs else [0]

    response = {
        "labels": json.dumps(labels),
        "statuses": json.dumps(statuses),
        "interval": interval,
        "intervals": INTERVALS.keys(),
    }
    # If HTMX requests partial update
    if request.htmx:
        return render(
            request,
            "monitoring/partials/postgres_data_partial.html",
            response,
        )

    # Initial full view
    return render(
        request,
        "monitoring/postgres_dashboard.html",
        response,
    )
