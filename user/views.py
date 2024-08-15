from django.forms import ValidationError
from django.shortcuts import render
from django.contrib.auth.hashers import check_password
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from user.models import CustomUser
from user.serializers import UserSerializer


# Create your views here.
class UserCreateAPIView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            # jwt
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            response = Response(
                {
                    "user": serializer.data,
                    "message": "Signup success",
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )

            response.set_cookie("access", access_token, httponly=True)
            response.set_cookie("refresh", refresh_token, httponly=True)

            return response
        except:
            response = {"message": "Signup failed", "errors": serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class AuthUserAPIView(APIView):
    def get(self, request):
        user = request.user

        if user is not None:
            return Response({"email": user.email}, status=status.HTTP_200_OK)

        return Response({"message": "해당 사용자가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]

        user = CustomUser.objects.filter(email=email).first()

        # 만약 username에 맞는 user가 존재하지 않는다면,
        if user is None:
            return Response({"message": "존재하지 않는 아이디입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 비밀번호가 틀린 경우,
        if not check_password(password, user.password):
            return Response({"message": "비밀번호가 틀렸습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # user가 맞다면,
        if user is not None:
            token = TokenObtainPairSerializer.get_token(user)  # refresh 토큰 생성
            refresh_token = str(token)  # refresh 토큰 문자열화
            access_token = str(token.access_token)  # access 토큰 문자열화
            response = Response(
                {
                    "user": UserSerializer(user).data,
                    "message": "login success",
                    "token": {"access": access_token, "refresh": refresh_token},
                },
                status=status.HTTP_200_OK,
            )

            response.set_cookie("access", access_token, httponly=True)
            response.set_cookie("refresh", refresh_token, httponly=True)
            return response
        else:
            return Response({"message": "로그인에 실패하였습니다."}, status=status.HTTP_400_BAD_REQUEST)


def index(request):
    return render(request, "register.html", context={})


def login(request):
    return render(request, "login.html", context={})
