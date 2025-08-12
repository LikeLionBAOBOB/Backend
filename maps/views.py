from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.functional import cached_property
from django.conf import settings
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import requests
from json import JSONDecodeError
import logging

from .serializers import LibraryLocationAndCongestionResponse, LibraryItemSerializer
from libraries.models import Library

BASE_URL = "http://data4library.kr/api/libSrch"

def fetch_lib_info_or_none(lib_code: int):
    """도서관 상세 정보를 가져오는 함수"""
    try:
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
    except Exception as e:
        logger.error(f"도서관 정보 조회 실패: {lib_code} - {e}")
        return None
from .utils.geocoding import geocode_query_cached  # 캐시 래퍼 사용

logger = logging.getLogger(__name__)

NAVER_GEOCODE_URL = "https://maps.apigw.ntruss.com/map-geocode/v2/geocode"
WORKERS = 6
TOTAL_TIME_BUDGET = 7.0  # 전체 응답 타임 박스(초)

def fetch_lib_location_by_name(name: str, use_cache: bool = True):
    """이름으로 지오코딩해서 (lat, lng) 반환. 캐시 우선."""
    if not name:
        logger.warning(f"지오코딩 실패: 이름이 없음 - {name}")
        return None

    # 1) 캐시 먼저
    if use_cache:
        try:
            results = geocode_query_cached(name) or []
            if results:
                x = float(results[0]["x"])  # lng
                y = float(results[0]["y"])  # lat
                logger.info(f"캐시에서 지오코딩 성공: {name} -> ({y}, {x})")
                return y, x
        except Exception as e:
            logger.warning(f"캐시 지오코딩 실패: {name} - {e}")

    # 2) 네이버 직접 호출 (빠른 타임아웃)
    try:
        res = requests.get(
            NAVER_GEOCODE_URL,
            params={"query": name},
            headers={
                "X-NCP-APIGW-API-KEY-ID": settings.NAVER_MAPS_CLIENT_ID,
                "X-NCP-APIGW-API-KEY": settings.NAVER_MAPS_CLIENT_SECRET,
            },
            timeout=2,  # 빠르게 실패
        )
        res.raise_for_status()
        data = res.json()
        logger.info(f"네이버 API 응답: {name} - status: {res.status_code}")
    except (requests.RequestException, JSONDecodeError) as e:
        logger.error(f"네이버 API 요청 실패: {name} - {e}")
        return None

    addrs = data.get("addresses", [])
    if not addrs:
        logger.warning(f"네이버 API 주소 없음: {name}")
        return None

    first = addrs[0]
    x = first.get("x") or (first.get("point") or {}).get("x")
    y = first.get("y") or (first.get("point") or {}).get("y")
    if x is None or y is None:
        logger.warning(f"네이버 API 좌표 없음: {name} - x:{x}, y:{y}")
        return None

    logger.info(f"네이버 지오코딩 성공: {name} -> ({float(y)}, {float(x)})")
    return float(y), float(x)


def infer_congestion_level(lib_code: int) -> int:
    return 2  # TODO 실제 로직으로 교체


def congestion_level_to_text(level: int) -> str:
    """congestion_level을 문자열로 변환"""
    mapping = {1: "여유", 2: "보통", 3: "혼잡"}
    return mapping.get(level, "보통")


class NearbyLibrariesView(APIView):
    """
    GET /maps/nearby/?lat=..&lng=..&lib_codes=1,2,3&limit=20&force_direct=0
    """
    class BadRequest(Exception): ...

    @cached_property
    def user_latlng(self):
        try:
            lat = float(self.request.query_params.get("lat"))
            lng = float(self.request.query_params.get("lng"))
        except (TypeError, ValueError):
            raise self.BadRequest("lat,lng 쿼리파라미터가 필요합니다.")
        return {"lat": lat, "lng": lng}

    def get_lib_queryset(self):
        codes_param = self.request.query_params.get("lib_codes")
        limit = int(self.request.query_params.get("limit", 50))
        qs = Library.objects.all()
        if codes_param:
            code_list = [c.strip() for c in codes_param.split(",") if c.strip()]
            qs = qs.filter(lib_code__in=code_list)
        return qs[:limit]

    def build_library_item(self, lib: Library, force_direct: bool = False):
        """Serializer에 맞는 dict 구성 - lib 객체를 포함한 구조로 변경"""
        logger.info(f"도서관 처리 시작: {lib.lib_code}")
        
        # 1차: 도서관 상세 정보 가져오기
        lib_info = fetch_lib_info_or_none(lib.lib_code)
        if not lib_info:
            logger.error(f"도서관 정보 조회 실패: {lib.lib_code}")
            return None
        
        # 도서관 이름 추출
        lib_name = lib_info.get("libName")
        if not lib_name:
            logger.warning(f"도서관 이름이 없음: {lib.lib_code}")
            lib_name = f"도서관_{lib.lib_code}"
        
        logger.info(f"도서관 정보 조회 성공: {lib.lib_code} - {lib_name}")

        # 도서관 이름으로 지오코딩 (주소가 있으면 주소 우선 사용)
        address = lib_info.get("address")
        geocode_query = address if address else lib_name
        
        logger.info(f"지오코딩 쿼리: {lib.lib_code} - '{geocode_query}' (address: {bool(address)})")
        coords = fetch_lib_location_by_name(geocode_query, use_cache=(not force_direct))
        if not coords:
            logger.error(f"지오코딩 실패: {lib.lib_code} - {lib_name}")
            return None

        lat, lng = coords
        level = infer_congestion_level(lib.lib_code)

        # Serializer가 기대하는 형태로 반환 - lib 객체를 포함
        result = {
            "lib": lib_info,  # 전체 lib_info 객체 포함
            "lat": lat,
            "lng": lng,
            "congestion_level": level,
        }
        
        logger.info(f"도서관 처리 성공: {lib.lib_code} -> lat={lat}, lng={lng}, congestion_level={level}")
        return result

    def build_library_item_safe(self, lib: Library, force_direct: bool = False):
        try:
            return self.build_library_item(lib, force_direct=force_direct)
        except Exception as e:
            logger.error(f"도서관 처리 중 예외 발생: {lib.lib_code} - {e}")
            return None

    def get(self, request):
        start = time.perf_counter()
        try:
            user_loc = self.user_latlng
            libraries_qs = self.get_lib_queryset()
            force_direct = request.query_params.get("force_direct") in ("1", "true", "True")

            logger.info(f"요청 처리 시작 - 총 {libraries_qs.count()}개 도서관")
            
            items = []
            futures = []

            with ThreadPoolExecutor(max_workers=WORKERS) as ex:
                for lib in libraries_qs:
                    futures.append(ex.submit(self.build_library_item_safe, lib, force_direct))

                # 전체 타임박스 내에서만 수거
                completed_count = 0
                for fut in as_completed(futures, timeout=TOTAL_TIME_BUDGET):
                    if time.perf_counter() - start > TOTAL_TIME_BUDGET:
                        logger.warning("시간 초과로 중단")
                        break
                    try:
                        item = fut.result(timeout=1.0)
                        completed_count += 1
                        if item:
                            items.append(item)
                    except Exception as e:
                        logger.error(f"Future 결과 처리 실패: {e}")

            logger.info(f"처리 완료: {completed_count}개 처리, {len(items)}개 성공")

            payload = {
                "user_location": {"lat": user_loc["lat"], "lng": user_loc["lng"]},
                "libraries": items,
            }
            
            serializer = LibraryLocationAndCongestionResponse(payload, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except self.BadRequest as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:
            return Response({"error": f"지오코딩 오류: {e}"}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}")
            return Response({"error": "서버 오류"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)