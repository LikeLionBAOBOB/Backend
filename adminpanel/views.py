from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from seats.detect_objects import detect_objects
from seats.views import load_rois, point_in_rect
from pathlib import Path
from .serializers import *
import json

PROJECT_ROOT = Path(__file__).parent.parent
IMAGES = PROJECT_ROOT / "media/images"
ROIS = PROJECT_ROOT / "seats/rois"

class ManagerLibraryView(APIView):
    def get(self, request):
        serializer = ManagerLibrarySerializer({})
        return Response(serializer.data)

# 전체 좌석 확인
class AdminSeatStatusView(APIView):
    def get(self, request):
        lib_code = "111257"
        img_name = "16.jpg"

        img_path = IMAGES / str(lib_code) / img_name
        seats = load_rois(lib_code, img_name)
        objects = detect_objects(str(img_path))

        results = []
        for seat in seats:
            found_person = False
            found_laptop = False
            for obj in objects:
                cx, cy = obj["center"]
                if point_in_rect(cx, cy, seat):
                    if obj["name"] == "person":
                        found_person = True
                    elif obj["name"] == "laptop":
                        found_laptop = True
            if found_person:
                status = "이용 중"
            elif found_laptop:
                status = "사석화"
            else:
                status = "이용 가능"
            results.append({
                "seat_id": seat["seat_id"],
                "status": status
            })
        
        serializer = AdminSeatStatusSerializer(results, many=True)
        return Response({"seats": serializer.data})