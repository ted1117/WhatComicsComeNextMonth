from typing import Any

from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import CustomUser


class UserService:
    def __init__(self, user_model, serializer_class, token_serializer):
        """
        UserService 초기화

        :param user_model: 사용자 모델
        :param serializer_class: 사용자 직렬화기 클래스
        :param token_serializer: 토큰 직렬화기 클래스
        """
        self.user_model = user_model
        self.serializer_class = serializer_class
        self.token_serializer = token_serializer

    def register_user(self, data) -> dict[str, Any]:
        """
        사용자 생성 및 토큰 발급

        :param data: 사용자 생성에 필요한 데이터
        :return: 사용자, 액세스 토큰, 리프레시 토큰
        """
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return {
            "user": serializer.data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    def login_user(self, data) -> dict[str, Any]:
        """
        사용자 로그인

        :param data: 로그인 데이터
        :return: email, 액세스 토큰, 리프레시 토큰
        """
        serializer = self.token_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        return {
            "email": validated_data["email"],
            "access_token": validated_data["access"],
            "refresh_token": validated_data["refresh"],
        }

    def logout_user(self, refresh) -> bool:
        """
        사용자 로그아웃

        :param refresh: 리프레시 토큰
        :return: 로그아웃 성공 여부
        """
        try:
            token = RefreshToken(refresh)
            token.blacklist()
            return True
        except (TokenError, InvalidToken):
            return False

    def deactivate_user(self, user) -> CustomUser:
        user.is_active = False
        user.save()
        return user
