from django import forms


class OpenWeatherForm(forms.Form):
    lat = forms.FloatField(label="Latitude", required=True)
    lon = forms.FloatField(label="Longitude", required=True)


class NetatmoForm(forms.Form):
    ne_lat = forms.FloatField(label="NE Latitude", required=True)
    ne_lon = forms.FloatField(label="NE Longitude", required=True)
    sw_lat = forms.FloatField(label="SW Latitude", required=True)
    sw_lon = forms.FloatField(label="SW Longitude", required=True)
