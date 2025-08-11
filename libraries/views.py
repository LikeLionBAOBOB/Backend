import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from typing import Dict, List, Tuple

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


# 도서관 검색 결과 조회
class LibrarySearchView(APIView):
    def get(self, request):
        q = request.query_params.get("q", "").strip()
        if not q:
            return Response({"message": "검색어가 누락되었습니다."}, status=status.HTTP_400_BAD_REQUEST)

        tokens = [t.strip() for t in q.split() if t.strip()]
        lib_codes = Library.objects.values_list("lib_code", flat=True)

        results = []
        for code in lib_codes:
            try:
                lib = fetch_lib_info_or_none(code)
                if not lib:
                    continue

                name = lib.get("libName", "")
                address = lib.get("address", "")
                if all(t in name or t in address for t in tokens):
                    results.append((lib, code))
            except requests.RequestException:
                continue

        if not results:
            return Response({"message": "검색 결과가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        results.sort(key=lambda x: x[0].get("libName", "").strip())
        data = SimpleLibrarySerializer(results, many=True, context={"request": request}).data
        return Response({"results": data}, status=status.HTTP_200_OK)