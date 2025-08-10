import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *

BASE_URL = "http://data4library.kr/api/libSrch"
LIB_CODES = [
    # 서대문구
    111179, # 남가좌새롬도서관
    111051, # 이진아기념도서관
    111252, # 홍은도담도서관
    # 마포구
    111086, # 마포구립 서강도서관
    711596, # 마포나루 스페이스
    111514, # 마포소금나루도서관
    111467, # 마포중앙도서관
    111257  # 해오름 작은도서관
]

# 도서관 정보 확인 (간략)
class LibrarySimpleView(APIView):
    def get(self, request, lib_code):
        if lib_code not in LIB_CODES:
            return Response({"error": "허용되지 않은 도서관 코드입니다."}, status=status.HTTP_404_NOT_FOUND)
        
        params = {
            "authKey": settings.LIBRARY_API_KEY,
            "libCode": lib_code,
            "format": "json"
        }

        try:
            res = requests.get(BASE_URL, params=params)
            res.raise_for_status()
            data = res.json()
            libs_data = data.get("response", {}).get("libs", [])
            if not libs_data:
                return Response({"error": "도서관 정보를 불러올 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            lib_info = libs_data[0]["lib"]
            serializer = SimpleLibrarySerializer((lib_info, lib_code), context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 도서관 정보 확인 (전체)
class LibraryDetailView(APIView):
    def get(self, request, lib_code):
        if lib_code not in LIB_CODES:
            return Response({"error": "허용되지 않은 도서관 코드입니다."}, status=status.HTTP_404_NOT_FOUND)
        
        params = {
            "authKey": settings.LIBRARY_API_KEY,
            "libCode": lib_code,
            "format": "json"
        }

        try:
            res = requests.get(BASE_URL, params=params)
            res.raise_for_status()
            data = res.json()
            libs_data = data.get("response", {}).get("libs", [])
            if not libs_data:
                return Response({"error": "도서관 정보를 불러올 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            lib_info = libs_data[0]["lib"]
            serializer = DetailLibrarySerializer((lib_info, lib_code), context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)