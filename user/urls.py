from django.urls import path

from user import views

from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

urlpatterns = [
    path("signup/", views.UserCreateAPIView.as_view()),
    path("register/", views.index, name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("signin/", views.AuthUserAPIView.as_view()),
    path("login/", views.login, name="login"),
]
