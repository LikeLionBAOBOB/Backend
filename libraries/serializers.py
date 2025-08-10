from rest_framework import serializers
from django.conf import settings
import json
from pathlib import Path

def load_library_info():
    data_path = Path(settings.BASE_DIR) / "libraries" / "data" / "library_info.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

LIBRARY_INFO = load_library_info()


# 도서관 정보 확인 (간략)
class SimpleLibrarySerializer(serializers.Serializer):
    name = serializers.CharField()
    image = serializers.CharField()
    current_seats = serializers.IntegerField()
    total_seats = serializers.IntegerField()
    congestion = serializers.CharField()
    is_open = serializers.CharField()
    operating_time = serializers.CharField()

    def to_representation(self, instance):
        lib, lib_code = instance
        current_hours = LIBRARY_INFO.get(str(lib_code), {}).get("current_hours", "")

        return {
            "name": lib.get("libName"),
            "image": f"{settings.MEDIA_URL}libraries/{lib_code}.png",  # lib_code는 views.py 참고
            "current_seats": 0,      # 실제 좌석 수 반영 -> 추후 수정 필요
            "total_seats": 0,        # 실제 좌석 수 반영 -> 추후 수정 필요
            "congestion": "보통",    # 혼잡도 계산 -> 추후 수정 필요
            "is_open": "운영 중",    # 현재 시간 2시로 고정
            "operating_time": current_hours
        }


# 도서관 정보 확인 (전체)
class DetailLibrarySerializer(serializers.Serializer):
    name = serializers.CharField()
    address = serializers.CharField()
    image = serializers.CharField()
    current_seats = serializers.IntegerField()
    total_seats = serializers.IntegerField()
    congestion = serializers.CharField()
    is_open = serializers.CharField()
    operating_time = serializers.CharField()
    detail_time = serializers.CharField()
    naver_map = serializers.CharField()
    site = serializers.CharField()

    def to_representation(self, instance):
        lib, lib_code = instance
        current_hours = LIBRARY_INFO.get(str(lib_code), {}).get("current_hours", "")
        detail_time = LIBRARY_INFO.get(str(lib_code), {}).get("weekly_hours", "")
        naver_map = LIBRARY_INFO.get(str(lib_code), {}).get("naver_map", "")
        site = LIBRARY_INFO.get(str(lib_code), {}).get("homepage", "")

        return {
            "name": lib.get("libName"),
            "address": lib.get("address"),
            "image": f"{settings.MEDIA_URL}libraries/{lib_code}.png",  # lib_code는 views.py 참고
            "current_seats": 0,      # 실제 좌석 수 반영 -> 추후 수정 필요
            "total_seats": 0,        # 실제 좌석 수 반영 -> 추후 수정 필요
            "congestion": "보통",    # 혼잡도 계산 -> 추후 수정 필요
            "is_open": "운영 중",    # 현재 시간 2시로 고정
            "operating_time": current_hours,
            "detail_time": detail_time,
            "naver_map": naver_map,
            "site": site
        }
