from django.contrib import admin


from .models import WeatherData, WeatherStation

admin.site.register(WeatherStation)
admin.site.register(WeatherData)

