from django.urls import path, include

from user import views

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView,
)

router = DefaultRouter()
router.register(r"", views.UserViewset, basename="user")

urlpatterns = [
    path("signup/", views.UserCreateAPIView.as_view()),
    path("token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("signin/", views.AuthUserAPIView.as_view()),
    path("", include(router.urls)),
    # templates
    # path("login/", views.login, name="login"),
    path("register/", views.index, name="register"),
]
