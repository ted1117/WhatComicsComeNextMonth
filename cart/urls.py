from django.urls import path

from cart.views import CartAPIView, CartListAPIView, cart

urlpatterns = [
    path("", CartAPIView.as_view()),
    path("list/", CartListAPIView.as_view()),
    path("index/", cart, name="cart"),
]
