from django.urls import path

from user import views

urlpatterns = [
    path("signup/", views.UserCreate.as_view()),
]
