from rest_framework import serializers


class LocationSerializer(serializers.Serializer):
    latitude = serializers.FloatField(
        min_value=-90,
        max_value=90,
    )
    longitude = serializers.FloatField(
        min_value=-180,
        max_value=180,
    )


class RouteRequestSerializer(serializers.Serializer):
    start = LocationSerializer()
    finish = LocationSerializer()