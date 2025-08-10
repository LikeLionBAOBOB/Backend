from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import *

class ManagerLibraryView(APIView):
    def get(self, request):
        serializer = ManagerLibrarySerializer({})
        return Response(serializer.data)