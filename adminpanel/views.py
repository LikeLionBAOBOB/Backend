from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from seats.detect_objects import detect_objects
from seats.views import load_rois, point_in_rect
from pathlib import Path
from .serializers import *
import json

PROJECT_ROOT = Path(__file__).parent.parent
IMAGES = PROJECT_ROOT / "media/images"
ROIS = PROJECT_ROOT / "seats/rois"

class ManagerLibraryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = ManagerLibrarySerializer({})
        return Response(serializer.data)

# 전체 좌석 확인
class AdminSeatStatusView(APIView):
    permission_classes = [IsAuthenticated]
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
    
# 도서관 혼잡도 정보
class AdminCongestionView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        lib_code = "111257"
        img_name = "16.jpg"

        img_path = IMAGES / str(lib_code) / img_name
        seats = load_rois(lib_code, img_name)
        objects = detect_objects(str(img_path))

        current_seats = 0
        total_seats = len(seats)

        for seat in seats:
            found = False
            for obj in objects:
                cx, cy = obj["center"]
                if point_in_rect(cx, cy, seat):
                    found = True
                    break
            if found:
                current_seats += 1

        if total_seats == 0:
            congestion = "여유"
        else:
            ratio = current_seats / total_seats * 100
            if ratio < 30:
                congestion = "여유"
            elif ratio < 70:
                congestion = "보통"
            else:
                congestion = "혼잡"
        
        data = {
            "current_seats": current_seats,
            "total_seats": total_seats,
            "congestion": congestion,
        }
        serializer = CongestionStatusSerializer(data)
        return Response(serializer.data)

# 좌석 로그 확인
LOG_IMAGES = [
    ("13.jpg", "13:00"),
    ("14.jpg", "13:20"),
    ("15.jpg", "13:40"),
    ("16.jpg", "14:00"),
]

class AdminSeatLogView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, seat_id):
        lib_code = "111257"

        logs = []
        prev_status = None
        count = 0   # 사석화 카운트

        for img_name, time_str in LOG_IMAGES:
            img_path = IMAGES / lib_code / img_name
            seats = load_rois(lib_code, img_name)
            objects = detect_objects(str(img_path))

            # 2번, 5번 좌석
            seat = next((s for s in seats if str(s["seat_id"]) == str(seat_id)), None)
            if not seat:
                continue

            found_person = False
            found_laptop = False
            for obj in objects:
                cx, cy = obj["center"]
                if point_in_rect(cx, cy, seat):
                    if obj["name"] == "person":
                        found_person = True
                    elif obj["name"] == "laptop":
                        found_laptop = True

            # 상태 결정
            if found_person:
                status = "이용 중"
            elif found_laptop:
                status = "사석화"
            else:
                status = "이용 가능"

            # 좌석 로그
            if (prev_status is None or prev_status in ["이용 중", "이용 가능"]) and status == "사석화":
                logs.append({"time": time_str, "status": "사석화가 시작되었습니다."})
                count = 1
            elif prev_status == "사석화" and status == "사석화":
                count += 1
                logs.append({"time": time_str, "status": "사석화가 진행중입니다."})
            # 직원이 짐 치우고 사석화 초기화
            elif prev_status == "사석화" and status != "사석화":
                count = 0
            prev_status = status
        logs.append({"time": "14:20", "status": "사석화가 60분 경과되었습니다."})

        serializer = AdminSeatLogSerializer({
            "seat_id": str(seat_id),
            "log": logs
        })
        return Response(serializer.data)