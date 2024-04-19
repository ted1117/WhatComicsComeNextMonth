from django.shortcuts import render

from rest_framework import generics, mixins, views, status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from manga.models import Manga


# Create your views here.
class CartAPIView(views.APIView):
    def get(self, request, *args, **kwargs):
        cart = request.session.get("cart", {})

        return Response(cart, status=status.HTTP_200_OK)

    def post(self, request, manga_id, *args, **kwargs):
        cart = request.session.get("cart", {})

        if manga_id not in cart:
            cart[manga_id] += 1

        return Response({"message": "만화가 장바구니에 추가되었습니다."}, status=status.HTTP_200_OK)

    def delete(self, request, manga_id=None):
        cart = request.session.get("cart")

        if manga_id:
            del cart[manga_id]
            request.session["cart"] = cart
            return Response({"message": "만화가 장바구니에서 삭제되었습니다."}, status=status.HTTP_200_OK)
        else:
            request.session["cart"] = {}
            return Response({"message": "장바구니가 초기화되었습니다."}, status=status.HTTP_200_OK)
