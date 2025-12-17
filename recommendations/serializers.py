from rest_framework import serializers
from vehicles.models import Vehicle
from vehicles.serializers import VehicleSerializer


class SimilarVehicleSerializer(serializers.Serializer):
    """
    Serializer for similar vehicle recommendations.
    Includes vehicle details and similarity score.
    """
    vehicle = VehicleSerializer()
    similarity_score = serializers.FloatField(
        help_text="Similarity score (0-100, higher is more similar)"
    )
    reason = serializers.CharField(
        help_text="Explanation of why this vehicle is similar"
    )
