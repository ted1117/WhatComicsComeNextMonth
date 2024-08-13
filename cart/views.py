from django.shortcuts import render

from rest_framework import generics, mixins, views, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

from cart.serializers import CartRetrieveSerializer, CartSerializer
from cart.models import Cart
from manga.models import Manga


# Create your views here.
class CartAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user)
        serializer = CartRetrieveSerializer(cart, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = CartSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "만화가 장바구니에 추가되었습니다."}, status=status.HTTP_200_OK)

        return Response(
            {"message": "만화가 장바구니에 담기지 않았습니다.\n다시 시도하세요."}, status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, *args, **kwargs):
        try:
            manga_id = request.GET.get("manga_id")
            comic = Cart.objects.get(user=request.user, manga_id=manga_id)
            comic.delete()

            return Response({"message": "만화가 장바구니에서 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

        except Cart.DoesNotExist:
            return Response({"message": "만화가 이미 장바구니에 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"message": "잘못된 접근입니다.", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
