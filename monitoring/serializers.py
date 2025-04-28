from datetime import datetime

from django.utils import timezone
from rest_framework import serializers

from .models import WeatherData, WeatherStation


class UnixTimestampField(serializers.Field):
    """Custom field to convert a Unix timestamp into a datetime object"""

    def to_internal_value(self, value):
        # Converts the timestamp into a datetime object with timezone
        return timezone.make_aware(datetime.fromtimestamp(value), timezone.utc)

    def to_representation(self, value):
        # Converts the datetime into a Unix timestamp for the JSON response
        return int(value.timestamp())


class WeatherStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherStation
        fields = "__all__"


class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        fields = "__all__"


class OpenWeatherSerializer(serializers.ModelSerializer):
    station = WeatherStationSerializer(read_only=True)
    # Explicit declaration of fields for the station
    station_name = serializers.CharField(write_only=True, source="name")
    source = serializers.CharField(write_only=True, default="openweather")
    source_id = serializers.CharField(write_only=True, source="id")
    longitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    latitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    locality = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = WeatherData
        fields = [
            "temperature",
            "feels_like",
            "humidity",
            "pressure",
            "station",
            "timestamp",
            "station_name",
            "source",
            "source_id",
            "longitude",
            "latitude",
            "locality",
        ]

    field_mapping = {
        "temperature": "main.temp",
        "feels_like": "main.feels_like",
        "humidity": "main.humidity",
        "pressure": "main.pressure",
        "timestamp": "dt",
        "longitude": "coord.lon",
        "latitude": "coord.lat",
    }

    def to_internal_value(self, data):
        """Maps OpenWeather JSON fields to Django fields."""
        mapped_data = {key: self.get_nested_value(data, path) for key, path in self.field_mapping.items()}
        ts_value = mapped_data.get("timestamp")
        try:
            ts_value = float(ts_value)
        except (TypeError, ValueError):
            raise serializers.ValidationError({"timestamp": "Invalid timestamp value."})
        mapped_data["timestamp"] = datetime.fromtimestamp(ts_value)
        mapped_data["station_name"] = self.get_nested_value(data, "name")
        mapped_data["source"] = "openweather"
        mapped_data["source_id"] = self.get_nested_value(data, "id")
        print(mapped_data)

        return super().to_internal_value(mapped_data)

    def get_nested_value(self, data, path):
        """Extracts nested values based on the JSON key."""
        print(f"Data_type: {type(data)}")
        keys = path.split(".")
        for key in keys:
            data = data.get(key, None)
            if data is None:
                break
        return data

    def create(self, validated_data):
        """Creates a WeatherData object associated with a WeatherStation object"""
        station_data = {
            "name": validated_data.pop("name"),
            "source": validated_data.pop("source"),
            "source_id": validated_data.pop("id"),
            "longitude": validated_data.pop("longitude", None),
            "latitude": validated_data.pop("latitude", None),
            "locality": validated_data.pop("locality", None),
        }
        # create or get the station
        station, _ = WeatherStation.objects.get_or_create(**station_data)
        # create the weather data
        weather_data = WeatherData.objects.create(station=station, **validated_data)
        return weather_data


class NetatmoSerializer(serializers.ModelSerializer):
    station = WeatherStationSerializer(read_only=True)
    # Explicit declaration of fields for the station
    source = serializers.CharField(write_only=True)
    source_id = serializers.CharField(write_only=True, source="_id")
    name = serializers.CharField(write_only=True)
    longitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    latitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    city = serializers.CharField(write_only=True, required=False, allow_null=True)
    locality = serializers.CharField(write_only=True, required=False, allow_null=True)
    street = serializers.CharField(write_only=True, required=False, allow_null=True)
    measures = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = WeatherData
        fields = [
            "temperature",
            "humidity",
            "pressure",
            "station",
            "timestamp",
            "name",
            "source",
            "source_id",
            "longitude",
            "latitude",
            "city",
            "street",
            "measures",
            "locality",
        ]

    field_mapping = {
        "longitude": "place.location[0]",
        "latitude": "place.location[1]",
        "city": "place.city",
        "street": "place.street",
        "measures": "measures",
        "source_id": "_id",
    }

    def to_internal_value(self, data):
        """Maps Netatmo JSON fields to Django fields."""
        mapped_data = {key: self.get_nested_value(data, path) for key, path in self.field_mapping.items()}
        for _, sub_item in mapped_data.pop("measures").items():
            print(f"measure: {sub_item}")
            if "type" in sub_item.keys():
                print(f"measure type: {sub_item['type']}")
                print(f"types number: {len(sub_item['type'])}")
                for index, metrics_type in enumerate(sub_item["type"]):
                    mapped_data[metrics_type] = next(iter(sub_item["res"].values()))[index]
                    ts_value = next(iter(sub_item["res"].keys()))
                    mapped_data["timestamp"] = datetime.fromtimestamp(float(ts_value))
        mapped_data["name"] = " - ".join([mapped_data.get("city"), mapped_data.get("street")])
        mapped_data["source"] = "netatmo"
        mapped_data["locality"] = mapped_data.pop("street")
        print(mapped_data)
        return super().to_internal_value(mapped_data)

    def get_nested_value(self, data, path):
        """Extracts nested values based on the JSON key."""
        keys = path.split(".")
        print(f"Data_type: {type(data)}")
        print(f"Keys: {keys}")
        for key in keys:
            data = data.get(key, None)
            if data is None:
                break
        return data

    def create(self, validated_data):
        """Creates a WeatherData object associated with a WeatherStation object"""
        station_data = {
            "name": validated_data.pop("name"),
            "source": validated_data.pop("source"),
            "source_id": validated_data.pop("_id"),
            "longitude": validated_data.pop("longitude", None),
            "city": validated_data.pop("city", None),
            "latitude": validated_data.pop("latitude", None),
            "locality": validated_data.pop("locality", None),
        }
        # create or get the station
        station, _ = WeatherStation.objects.get_or_create(**station_data)
        # create the weather data
        weather_data = WeatherData.objects.create(station=station, **validated_data)
        return weather_data
