from django.urls import path

from cart.views import CartAPIView, cart

urlpatterns = [
    path("", CartAPIView.as_view()),
    path("index/", cart, name="cart"),
]
