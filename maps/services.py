from libraries.models import Library
from .utils import fetch_lib_info_or_none, naver_geocoding_address_to_coords
from django.core.cache import cache
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class LibraryService:
    @staticmethod
    def get_library_with_coordinates(library_code: str) -> Optional[Dict[str, Any]]:
        """단일 도서관 정보를 좌표와 함께 가져오기"""
        library_code = library_id
        # 캐시 확인
        cache_key = f"library_coords_{library_code}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # 도서관 기본 정보 가져오기
        lib_info = fetch_lib_info_or_none(library_code)
        if not lib_info:
            return None
        
        # 주소를 좌표로 변환
        coordinates = None
        if lib_info.get('address'):
            coordinates = naver_geocoding_address_to_coords(lib_info['address'])
        
        if coordinates:
            lat, lng = coordinates
            library_data = {
                'code': library_code,
                'name': lib_info['name'],
                'address': lib_info['address'],
                'phone': lib_info.get('phone', ''),
                'latitude': lat,
                'longitude': lng,
            }
            
            # 성공한 경우에만 캐시 저장 (1시간)
            cache.set(cache_key, library_data, 3600)
            return library_data
        else:
            logger.warning(f"주소를 좌표로 변환할 수 없음: {library_code} - {lib_info.get('address')}")
            return None
    
    @staticmethod
    def get_all_library_info_with_coords() -> List[Dict[str, Any]]:
        """모든 도서관의 상세 정보를 가져오고 좌표도 확보"""
        libraries = Library.objects.all()
        library_data = []
        
        for library in libraries:
            library_info = LibraryService.get_library_with_coordinates(library.library_code)
            if library_info:
                library_info['id'] = library.id  # DB ID 추가
                library_data.append(library_info)
        
        return library_data
    
    @staticmethod
    def get_libraries_with_distance(user_lat: float, user_lng: float, max_distance_km: float = 10.0) -> List[Dict[str, Any]]:
        """사용자 위치 기반으로 거리를 계산한 도서관 목록 반환"""
        from .utils import calculate_distance
        
        library_data = LibraryService.get_all_library_info_with_coords()
        
        # 거리 계산 및 필터링
        nearby_libraries = []
        for library in library_data:
            distance = calculate_distance(
                user_lat, user_lng,
                library['latitude'], library['longitude']
            )
            
            # 최대 거리 내의 도서관만 포함
            if distance <= max_distance_km:
                library['distance'] = round(distance, 2)
                nearby_libraries.append(library)
        
        # 거리순 정렬
        nearby_libraries.sort(key=lambda x: x['distance'])
        
        return nearby_libraries