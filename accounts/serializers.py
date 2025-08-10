import re
from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

class UserLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)

    def validate(self, data):
        phone = data.get('phone', None)

        user = User.objects.filter(phone=phone, role="user").first()

        if not user or not phone:
            raise serializers.ValidationError({"error": "전화번호가 일치하지 않습니다."})
        else:
            token = RefreshToken.for_user(user)
            refresh = str(token)
            access = str(token.access_token)

            data = {
                "access_token": access,
                "refresh_token": refresh,
                "data": {
                    "name": user.nickname
                },
            }
            return data


class ManagerLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=64)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        if User.objects.filter(email=email, role="manager").exists():
            user = User.objects.get(email=email, role="manager")
            if not user.check_password(password):
                raise serializers.ValidationError({"error": "이메일 또는 비밀번호가 일치하지 않습니다."})
            else:
                token = RefreshToken.for_user(user)
                refresh = str(token)
                access = str(token.access_token)

                data = {
                    "access_token": access,
                    "refresh_token": refresh,
                    "data": {
                        "name": user.nickname
                    }
                }
                return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=False)

    def validate(self, attrs):
        user = self.context["request"].user

        # 해당 유저의 모든 refresh 토큰을 블랙리스트 처리
        for token in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=token)

        return {
            "message": "성공적으로 로그아웃되었습니다."
        }