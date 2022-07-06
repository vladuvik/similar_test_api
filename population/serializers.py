from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from population.utils import CoordinatePoint


class PopulationReportSerializer(serializers.Serializer):
    radius = serializers.FloatField(min_value=0.1, required=True)
    longitude = serializers.FloatField(required=True)
    latitude = serializers.FloatField(required=True)

    def validate(self, attrs):
        lon, lat = attrs.get('longitude'), attrs.get('latitude')
        starting_coordinate = CoordinatePoint(
            longitude=lon,
            latitude=lat
        )

        if not starting_coordinate.is_valid():
            raise ValidationError(_(
                'Provided coordinates are not correct.'
            ))

        return attrs


class SimpleTaskSerializer(serializers.Serializer):
    task_id = serializers.UUIDField()
    status = serializers.CharField()
