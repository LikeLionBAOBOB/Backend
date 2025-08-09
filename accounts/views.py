from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import *

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = UserLoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        u = s.validated_data["user"]
        return Response({
            "access_token": s.validated_data["access_token"],
            "refresh_token": s.validated_data["refresh_token"],
            "data": {
                "name": getattr(u, "nickname", "")
            },
        }, status=status.HTTP_200_OK)


class ManagerLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = ManagerLoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        u = s.validated_data["user"]
        return Response({
            "access_token": s.validated_data["access_token"],
            "data": {
                "name": getattr(u, "nickname", "") or getattr(u, "email", ""),
            },
        }, status=status.HTTP_200_OK)
