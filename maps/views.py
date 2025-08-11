from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import json, time
import redis

r = redis.Redis.from_url(getattr(settings, "REDIS_URL", "redis://localhost:6379/0"))

CONGESTION_MAP = { 1: "여유", 2: "보통", 3: "혼잡"}

# Create your views here.

class NearbyLibraries(APIView):
    """
    GET /libraries/nearby?lat=37.55&lng=126.93&radius=3000
    응답: [{id, lat, lng, congestion, congestion_level}, ...]
    """
    def get(self, request):
        try:
            lat = float(request.query_params.get("lat"))
            lng = float(request.query_params.get("lng"))
            radius = int(request.query_params.get("radius", 3000))
        except ( TypeError, ValueError ):
            return Response({"detail": "lat, lng, radius 파라미터를 확인하세요."}, status=400)
