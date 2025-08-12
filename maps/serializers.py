from rest_framework import serializers

# 개별 도서관 위치 및 혼잡도
class LibraryItemSerializer(serializers.Serializer):
    library_id = serializers.IntegerField()
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    congestion = serializers.CharField()
    congestion_level = serializers.IntegerField()

    CONGESTION_MAP = {
        1: "여유",
        2: "보통",
        3: "혼잡",
    }

    def get_congestion(self, obj):
        # obj["congestion_level"]을 문자열로 변환
        return self.CONGESTION_MAP.get(obj.get("congestion_level"), "보통")

    def to_representation(self, instance):
        """
        instance 예시:
        {
            "lib": {... data4library 응답의 lib 객체 ...},
            "lat": 37.5663,
            "lng": 126.9779,
            "congestion_level": 1
        }
        """
        lib = instance.get("lib", {})
        return {
            "id": str(lib.get("libCode") or lib.get("id") or ""),
            "name": lib.get("libName"),
            "lat": float(instance.get("lat")),
            "lng": float(instance.get("lng")),
            "congestion": self.get_congestion(instance),
            "congestion_level": int(instance.get("congestion_level", 2)),
        }


# 최상위 응답
class LibraryLocationAndCongestionResponse(serializers.Serializer):
    user_location = serializers.DictField()  # {"lat": 37.5665, "lng": 126.9780}
    libraries = LibraryItemSerializer(many=True)
