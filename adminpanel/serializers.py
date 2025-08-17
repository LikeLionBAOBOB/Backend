from rest_framework import serializers
from django.conf import settings

class ManagerLibrarySerializer(serializers.Serializer):
    name = serializers.SerializerMethodField()
    
    def get_name(self, obj):
        return settings.DEFAULT_MANAGER_LIBRARY_NAME

class AdminSeatStatusSerializer(serializers.Serializer):
    seat_id = serializers.CharField()
    status = serializers.CharField()