from decimal import Decimal

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from archive.models import Rating
from archive.serializers import RatingRetrieveSerializer, RatingSerializer
from archive.services import RatingService
from user.authentication import CustomJWTAuthentication


# Create your views here.
class RatingPageNumberPagination(PageNumberPagination):
    page_size: int = 20
    page_size_query_param: str = "page_size"
    max_page_size: int = 100


class RatingViewSet(ModelViewSet):
    queryset = Rating.objects
    serializer_class = RatingSerializer
    pagination_class = RatingPageNumberPagination
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [AllowAny]

    rating_service = RatingService()

    def get_permissions(self):
        if self.action in ("create", "destroy"):
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        comic_id = self.request.query_params.get("comic_id")
        user_id = self.request.query_params.get("user_id")

        if comic_id and user_id:
            queryset = self.queryset.filter(comic=comic_id, user=user_id)
        elif comic_id:
            queryset = self.queryset.filter(comic=comic_id)
        elif user_id:
            queryset = self.queryset.filter(user=user_id)
        else:
            queryset = self.queryset.all()

        return queryset

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return RatingRetrieveSerializer
        return RatingSerializer

    def create(self, request, *args, **kwargs):
        comic_id = request.data.get("comic_id")
        if not comic_id:
            return Response(
                {"error": "comic_id not found."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            rating = self.rating_service.create_rating(
                comic_id=comic_id,
                user=request.user,
                rating=Decimal(request.data.get("rating", 0.0)),
                comment=request.data.get("comment", ""),
            )

            serializer = self.get_serializer(instance=rating)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            raise ValidationError(detail=str(e))
