from django.urls import path

from .views import (monitor_view, postgres_dashboard, postgres_status_page,
                    postgres_status_view, task_dashboard, task_stats_partial,
                    temperature_dashboard, temperature_data_partial)

urlpatterns = [
    path("form/", monitor_view, name="monitor_view"),
    path("dashboard/", task_dashboard, name="task_dashboard"),
    path("dashboard/stats", task_stats_partial, name="task_stats_partial"),
    path("temperature/", temperature_dashboard, name="temperature_dashboard"),
    path("temperature/data/", temperature_data_partial, name="temperature_data_partial"),
    path("postgres/", postgres_status_page, name="postgres_status_page"),
    path("postgres_status/", postgres_status_view, name="postgres_status_view"),
    path("postgres/dashboard/", postgres_dashboard, name="postgres_dashboard"),
]
