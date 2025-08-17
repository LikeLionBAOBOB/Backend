from rest_framework import serializers
from django.conf import settings

class ManagerLibrarySerializer(serializers.Serializer):
    name = serializers.SerializerMethodField()
    
    def get_name(self, obj):
        return settings.DEFAULT_MANAGER_LIBRARY_NAME

# 전체 좌석 확인
class AdminSeatStatusSerializer(serializers.Serializer):
    seat_id = serializers.CharField()
    status = serializers.CharField()

# 도서관 혼잡도 정보
class CongestionStatusSerializer(serializers.Serializer):
    current_seats = serializers.IntegerField()
    total_seats = serializers.IntegerField()
    congestion = serializers.CharField()