# utils/geocoding.py
import requests
from django.conf import settings
from functools import lru_cache

NAVER_GEOCODE_URL = "https://maps.apigw.ntruss.com/map-geocode/v2/geocode"

@lru_cache(maxsize=512)
def geocode_query_cached(query: str):
    """
    네이버 지도 지오코딩 API 호출 후 결과를 캐싱하여 반환.
    결과 형식:
    [
        {"x": "126.978275264", "y": "37.566642129", ...},
        ...
    ]
    """
    if not query:
        return []

    try:
        res = requests.get(
            NAVER_GEOCODE_URL,
            params={"query": query},
            headers={
                "X-NCP-APIGW-API-KEY-ID": settings.NAVER_MAPS_CLIENT_ID,
                "X-NCP-APIGW-API-KEY": settings.NAVER_MAPS_CLIENT_SECRET,
            },
            timeout=3,  # 3초 제한
        )
        res.raise_for_status()
        data = res.json()
    except requests.RequestException:
        return []

    return data.get("addresses", [])
