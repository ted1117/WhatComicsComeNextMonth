from typing import Dict, Any

from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

from user.authentication import CustomJWTAuthentication
from user.models import CustomUser
from user.permissions import IsAdminOrOwner
from user.serializers import CustomTokenObtainPairSerializer, UserSchema, UserSerializer
from user.services import UserService


# Create your views here.
class UserViewset(viewsets.ModelViewSet):
    """
    사용자 관리 Viewset
    ----
    사용자 계정에 CRUD 기능 제공
    - 회원 가입
    - 회원 목록 조회
    - 회원 정보 상세 조회
    - 회원 비활성화
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserSchema

    def __init__(self, *args, **kwargs):
        """
        UserViewset 초기화
        """
        super().__init__(*args, **kwargs)

        self.user_service = UserService(
            user_model=CustomUser,
            serializer_class=UserSerializer,
            token_serializer=CustomTokenObtainPairSerializer,
        )

    def get_authenticators(self):
        """
        요청에 따라 인증 클래스 결정

        POST 요청(회원가입)은 인증을 건너뛴다.
        """
        if not self.request or not hasattr(self.request, "method"):
            # drf-spectacular에서 호출될 때 Mock Request를 처리
            return [CustomJWTAuthentication()]

        if self.request.method == "post":
            return []
        return [CustomJWTAuthentication()]

    def get_permissions(self):
        """
        요청된 action에 따라 권한 설정

        - create: 누구나 접근 가능 (회원가입)
        - list: 관리자만 접근 가능
        - 기타: 관리자 혹은 본인만 접근 가능
        """
        if self.action == "create":
            return [AllowAny()]
        elif self.action == "list":
            return [IsAdminUser()]
        else:
            return [IsAdminOrOwner()]

    def create(self, request):
        """
        회원가입 처리.
        ----
        새 사용자를 등록하고 사용자 정보와 액세스/리프레시 토큰을 반환합니다.
        """
        try:
            result = self.user_service.register_user(request.data)
            response = Response(
                {
                    "user": result["user"],
                    "message": "Signup success",
                    "token": {
                        "access": result["access"],
                        "refresh": result["refresh"],
                    },
                },
                status=status.HTTP_200_OK,
            )

            response.set_cookie(
                key="access",
                value=result["access"],
                httponly=True,
                secure=True,
                samesite="Lax",
            )
            response.set_cookie(
                key="refresh",
                value=result["refresh"],
                httponly=True,
                secure=True,
                samesite="Lax",
            )

            return response
        except Exception as e:
            return Response(
                {
                    "message": "Signup failed",
                    "errors": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk=None):
        """
        사용자 계정 비활성화.
        ----
        사용자는 자신의 계정만 비활성화할 수 있으며, 관리자는 이를 수행할 수 없습니다.
        """
        if pk != str(request.user.pk):
            return Response(
                {"message": "권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = request.COOKIES.get("refresh")
        user = request.user

        self.user_service.deactivate_user(user)
        self.user_service.logout_user(refresh)

        response = Response(
            {"message": "계정이 비활성화됐습니다."}, status=status.HTTP_200_OK
        )

        response.delete_cookie("access")
        response.delete_cookie("refresh")

        return response


class UserLoginView(APIView):
    """
    사용자 로그인 APIView.
    ----
    사용자 인증 후 액세스 토큰과 리프레시 토큰을 반환합니다.
    """

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def __init__(self, **kwargs: Any):
        """
        UserLoginView 초기화.
        ----
        """
        super().__init__(**kwargs)
        self.user_service = UserService(
            user_model=CustomUser,
            serializer_class=None,
            token_serializer=CustomTokenObtainPairSerializer,
        )

    def post(self, request):
        """
        사용자 로그인 처리.
        ----
        사용자 인증 후 액세스 토큰과 리프레시 토큰을 반환하고, 이를 쿠키에 저장
        """
        try:
            result = self.user_service.login_user(request.data)
            response = Response(
                {
                    "user": result["email"],
                    "message": "로그인 성공",
                    "token": {
                        "access": result["access_token"],
                        "refresh": result["refresh_token"],
                    },
                },
                status=status.HTTP_200_OK,
            )
            # 쿠키에 토큰 저장
            response.set_cookie(
                key="access",
                value=result["access_token"],
                httponly=True,
                secure=True,
                samesite="Lax",
            )
            response.set_cookie(
                key="refresh",
                value=result["refresh_token"],
                httponly=True,
                secure=True,
                samesite="Lax",
            )
            return response
        except Exception as e:
            return Response(
                {"message": "로그인 실패", "errors": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserLogoutView(APIView):
    """
    사용자 로그아웃 APIView.
    ----
    리프레시 토큰을 무효화하고 쿠키를 삭제하여 로그아웃을 처리
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def __init__(self, **kwargs: Any):
        """
        UserLogoutView 초기화.
        """
        super().__init__(**kwargs)
        self.user_service = UserService(
            user_model=CustomUser,
            serializer_class=None,
            token_serializer=CustomTokenObtainPairSerializer,
        )

    def post(self, request):
        """
        사용자 로그아웃 처리
        ----
        리프레시 토큰을 무효화하고 액세스/리프레시 쿠키를 삭제
        """
        refresh_token = request.COOKIES.get("refresh")
        if not refresh_token:
            return Response(
                {"message": "로그아웃 실패: 리프레시 토큰이 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not self.user_service.logout_user(refresh_token):
            return Response(
                {"message": "유효하지 않은 리프레시 토큰입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = Response({"message": "로그아웃 성공"}, status=status.HTTP_200_OK)
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response


def index(request):
    return render(request, "register.html", context={})


def login(request):
    return render(request, "login.html", context={})
