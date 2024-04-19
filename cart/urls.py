from django.urls import path

from cart.views import CartAPIView

urlpatterns = [
    path("", CartAPIView.as_view()),
]
