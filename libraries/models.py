from django.db import models
from django.conf import settings

class Library(models.Model):
    ''' 해당 값들은 API에서 불러올 거기 때문에 주석 처리
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
    '''

    lib_code = models.IntegerField(unique=True, db_index=True)

    def __str__(self):
        return str(self.lib_code)


class UserPin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_pins')
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='library_pins')

    class Meta:
        unique_together = ('user', 'library')

    def __str__(self):
        return f"{self.user.nickname} - {self.library.lib_code}"