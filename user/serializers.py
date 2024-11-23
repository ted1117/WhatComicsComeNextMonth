from typing import Any, Dict

from user.models import CustomUser
from user.validators import EmailValidator, PasswordValidator
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[EmailValidator()])
    password = serializers.CharField(write_only=True, validators=[PasswordValidator()])
    password2 = serializers.CharField(write_only=True, min_length=4)

    class Meta:
        model = CustomUser
        fields = ["email", "password", "password2"]

    def validate(self, attrs) -> str:
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return attrs

    def create(self, validated_data) -> CustomUser:
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
        )

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, user)

        return user


class UserSchema(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "nickname",
            "email",
            "is_active",
            "is_superuser",
            "is_staff",
            "last_login",
        ]
        read_only_fields = ["nickname", "email", "is_superuser", "last_login"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs: Dict[str, str]) -> Dict[str, str]:
        email: str = attrs.get("email")  # type: ignore
        password: str = attrs.get("password")  # type: ignore

        if not email:
            raise serializers.ValidationError("이메일을 입력하십시오.")
        if not password:
            raise serializers.ValidationError("비밀번호를 입력하십시오.")

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )
        if not user:
            raise serializers.ValidationError(
                "이메일 또는 비밀번호가 올바르지 않습니다."
            )
        if not user.is_active:
            raise serializers.ValidationError(
                "계정이 비활성화됐습니다. 관리자에게 문의하세요."
            )

        data = super().validate(attrs)

        refresh = self.get_token(user)

        data["email"] = email
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, user)

        return data
