from django.urls import path, include

from user import views

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"", views.UserViewset, basename="user")

urlpatterns = [
    path("login/", views.UserLoginView.as_view()),
    path("logout/", views.UserLogoutView.as_view()),
    path("check-login-status/", views.check_login_status, name="check_login_status"),
    path("", include(router.urls)),
]
