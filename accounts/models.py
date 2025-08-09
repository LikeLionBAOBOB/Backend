from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', '일반 사용자'),
        ('manager', '사서'),
    )

    nickname = models.CharField(max_length=30, unique=True, null=False, blank=False)  # 사용자 닉네임 (책읽는 시민, 김이화 사서)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)  # 일반 로그인 (010-1234-5678)
    email = models.EmailField(unique=True, null=True, blank=True)  # 사서 로그인 (librarian@lib.or.kr)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')  # 사용자 역할 (일반 사용자, 사서)

    def __str__(self):
        return self.nickname