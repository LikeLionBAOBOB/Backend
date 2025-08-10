import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *

BASE_URL = "http://data4library.kr/api/libSrch"

def fetch_lib_info_or_none(lib_code: int):
    params = {
        "authKey": settings.LIBRARY_API_KEY,
        "libCode": lib_code,
        "format": "json",
    }
    res = requests.get(BASE_URL, params=params, timeout=5)
    res.raise_for_status()
    data = res.json()
    libs_data = data.get("response", {}).get("libs", [])
    if not libs_data:
        return None
    return libs_data[0]["lib"]


# 도서관 정보 확인 (간략)
class LibrarySimpleView(APIView):
    def get(self, request, lib_code: int):
        if not Library.objects.filter(lib_code=lib_code).exists():
            return Response({"error": "허용되지 않은 도서관 코드입니다."}, status=status.HTTP_404_NOT_FOUND)

        try:
            lib_info = fetch_lib_info_or_none(lib_code)
            if not lib_info:
                return Response({"error": "도서관 정보를 불러올 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            serializer = SimpleLibrarySerializer((lib_info, lib_code), context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 도서관 정보 확인 (전체)
class LibraryDetailView(APIView):
    def get(self, request, lib_code: int):
        if not Library.objects.filter(lib_code=lib_code).exists():
            return Response({"error": "허용되지 않은 도서관 코드입니다."}, status=status.HTTP_404_NOT_FOUND)

        try:
            lib_info = fetch_lib_info_or_none(lib_code)
            if not lib_info:
                return Response({"error": "도서관 정보를 불러올 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            serializer = DetailLibrarySerializer((lib_info, lib_code), context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)