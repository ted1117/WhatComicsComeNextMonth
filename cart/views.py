from django.shortcuts import render

from rest_framework import generics, mixins, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication

from cart.serializers import CartRetrieveSerializer, CartSerializer
from cart.models import Cart


# Create your views here.
class CartAPIView(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs) -> Response:
        cart = Cart.objects.filter(user=request.user)
        serializer = CartRetrieveSerializer(cart, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs) -> Response:
        serializer = CartSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "만화가 장바구니에 추가되었습니다."}, status=status.HTTP_200_OK)

        return Response(
            {"message": "만화가 장바구니에 담기지 않았습니다.\n다시 시도하세요."}, status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, *args, **kwargs) -> Response:
        try:
            comics = request.data.get("comics")
            deleted_comics = Cart.objects.filter(user=request.user, comic_id__in=comics)
            deleted_comics.delete()

            return Response({"message": "만화가 장바구니에서 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

        except Cart.DoesNotExist:
            return Response({"message": "만화가 이미 장바구니에 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"message": "잘못된 접근입니다.", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CartPageNumberPagination(PageNumberPagination):
    page_size: int = 20
    page_size_query_param: str = "page_size"
    max_page_size: int = 100


class CartListAPIView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = CartRetrieveSerializer
    pagination_class = CartPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Cart.objects.none()
        return Cart.objects.filter(user=user)


def cart(request):
    return render(request, "cart.html", context={})
