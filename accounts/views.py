from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import *

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data)
        return Response(serializer.errors)


class ManagerLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ManagerLoginSerializer

    def post(self, request):
        serializer = ManagerLoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data)
        return Response(serializer.errors)
