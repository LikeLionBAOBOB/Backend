import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.db import IntegrityError
from .models import *
from rest_framework.permissions import IsAuthenticated

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

'''
# 주소 반환용 이름 가져오는 api

def fetch_lib_name_or_none(lib_code: int):
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
    return libs_data[0]["lib"]["libName"]
'''

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


# 즐겨찾기 추가 및 삭제
class ToggleFavorite(APIView):
    permission_classes = [IsAuthenticated]

    def _get_library_or_404(self, lib_code: int):
        try:
            # 존재하는 도서관만 허용
            return Library.objects.get(lib_code=lib_code)
        except Library.DoesNotExist:
            return None

    def post(self, request, lib_code):
        library = self._get_library_or_404(lib_code)
        if library is None:
            return Response(
                {"detail": "존재하지 않는 도서관 코드입니다.", "library_id": lib_code},
                status=status.HTTP_404_NOT_FOUND
            )

        pin, created = UserPin.objects.get_or_create(user=request.user, library=library)
        return Response(
            {
                "is_favorite": True,
                "created": created,            # true면 이번에 새로 추가
                "library_id": lib_code,
                "message": "즐겨찾기에 추가되었습니다." if created else "이미 즐겨찾기에 있습니다."
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    def delete(self, request, lib_code):
        library = self._get_library_or_404(lib_code)
        if library is None:
            return Response(
                {"detail": "존재하지 않는 도서관 코드입니다.", "library_id": lib_code},
                status=status.HTTP_404_NOT_FOUND
            )

        deleted, _ = UserPin.objects.filter(user=request.user, library=library).delete()
        return Response(
            {
                "is_favorite": False,
                "deleted": bool(deleted),      # false면 원래 없던 상태
                "library_id": lib_code,
                "message": "즐겨찾기에서 삭제되었습니다." if deleted else "즐겨찾기에 없었습니다."
            },
            status=status.HTTP_200_OK
        )


# 즐겨찾기 목록 확인
class ViewFavoriteLibraries(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pins = (UserPin.objects
                .filter(user=request.user)
                .select_related('library')
                .order_by('-id'))

        items = []
        for pin in pins:
            code = pin.library.lib_code  # int
            lib_info = fetch_lib_info_or_none(code) or {"libName": str(code)}  # 캐시 키가 str라면 str로
            # SimpleLibrarySerializer는 lib.get("libName")를 참조하므로 키 맞춰줌
            items.append((lib_info, code))

        serializer = SimpleLibrarySerializer(items, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


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