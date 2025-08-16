from rest_framework.views import APIView
from rest_framework.response import Response
from .detect_objects import detect_objects
from .serializers import *
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).parent.parent  # BACKEND 폴더
IMAGES = PROJECT_ROOT / "media/images"  # BACKEND/media/images 폴더
ROIS = PROJECT_ROOT / "seats/rois"  # BACKEND/seats/rois 폴더

# rois/<lib_code>.json 불러오기 (없으면 기본 구조 반환)
def load_rois(lib_code, img_path):
    roi_path = ROIS / f"{lib_code}.json"
    with open(roi_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["images"][img_path]["seats"]

# 좌표가 주어진 사각형 안에 점이 있는지 확인
def point_in_rect(cx, cy, rect):
    if cx < rect["x"]:
        return False
    if cy < rect["y"]:
        return False
    if cx > rect["x"] + rect["w"]:
        return False
    if cy > rect["y"] + rect["h"]:
        return False
    return True

# 실시간 좌석 확인
class SeatStatusView(APIView):
    def get(self, request, lib_code):
        # 해오름 작은 도서관(111257)의 경우 16.jpg 이미지가 가장 최근
        if str(lib_code) == "111257":
            img_name = "16.jpg"
        else:
            img_name = "1.jpg"

        img_path = IMAGES / str(lib_code) / img_name
        seats = load_rois(lib_code, img_name)
        objects = detect_objects(str(img_path))

        results = []
        for seat in seats:
            found = False
            for obj in objects:
                cx, cy = obj["center"]
                if point_in_rect(cx, cy, seat):
                    found = True
                    break
            results.append({
                "seat_id": seat["seat_id"],
                "status": "이용 중" if found else "이용 가능"
            })
        
        serializer = SeatStatusSerializer(results, many=True)
        return Response({"seats": serializer.data})