from django.db import models


class WeatherStation(models.Model):
    SOURCE_CHOICES = [("openweather", "OpenWeather"), ("netatmo", "Netatmo")]

    name = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    locality = models.CharField(max_length=100, null=True, blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    source_id = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"


class WeatherData(models.Model):
    station = models.ForeignKey(WeatherStation, on_delete=models.CASCADE)
    temperature = models.FloatField()
    feels_like = models.FloatField(null=True, blank=True)  # Only OpenWeather
    humidity = models.IntegerField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ["-timestamp"]


class PostgresStatusLog(models.Model):
    STATUS_CHOICES = [
        ("up", "UP"),
        ("down", "DOWN"),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.timestamp} - {self.get_status_display()}"
