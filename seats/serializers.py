from rest_framework import serializers

class SeatStatusSerializer(serializers.Serializer):
    seat_id = serializers.CharField()
    status = serializers.CharField()