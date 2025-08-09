import re
from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken

def _normalize_phone(phone: str) -> str:
    return re.sub(r"\D", "", phone or "")


class UserLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)

    def validate(self, attrs):
        raw_phone = attrs["phone"].strip()
        phone = _normalize_phone(raw_phone)
        if not phone:
            raise serializers.ValidationError({"error": "전화번호는 모두 입력해야 합니다."})

        user = User.objects.filter(phone=phone).first()
        if not user or getattr(user, "role", None) != "user":
            raise serializers.ValidationError({"error": "전화번호가 일치하지 않습니다."})

        token = RefreshToken.for_user(user)
        attrs["user"] = user
        attrs["access_token"] = str(token.access_token)
        attrs["refresh_token"] = str(token)
        return attrs


class ManagerLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=64)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs):
        email = (attrs.get("email") or "").strip()
        password = (attrs.get("password") or "").strip()
        if not email or not password:
            raise serializers.ValidationError({"error": "email과 password는 모두 입력해야 합니다."})

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "email 또는 password가 일치하지 않습니다."})
        
        if getattr(user, "role", None) != "manager" or not getattr(user, "is_active", True):
            raise serializers.ValidationError({"error": "email 또는 password가 일치하지 않습니다."})

        if not user.check_password(password):
            raise serializers.ValidationError({"error": "email 또는 password가 일치하지 않습니다."})
        
        token = RefreshToken.for_user(user)
        attrs["user"] = user
        attrs["access_token"] = str(token.access_token)
        attrs["refresh_token"] = str(token)

        return attrs