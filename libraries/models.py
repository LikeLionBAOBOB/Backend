from django.db import models

class Library(models.Model):
    title = models.CharField(max_length=30, null=False)  # 도서관 이름
    seats_all = models.IntegerField(null=False)  # 전체 좌석 수
    is_closed = models.BooleanField(null=False)  # 운영 여부
    worktime = models.TextField(null=False)  # 운영시간
    map_url = models.TextField(null=False)  # 네이버 지도 연동 링크
    service_text = models.CharField(max_length=50, null=False)  # 편의시설 및 서비스
    address = models.CharField(max_length=50, null=False)  # 주소
    latitude = models.FloatField(null=False)  # 위도
    longitude = models.FloatField(null=False)  # 경도
    image = models.URLField(null=False)  # 도서관 이미지
    library_link = models.TextField(null=False)  # 도서관 링크

    def __str__(self):
        return self.title
