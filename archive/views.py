from decimal import Decimal

from django.db.models import Avg
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from archive.models import Rating
from archive.serializers import (
    RatingRetrieveSerializer,
    RatingSerializer,
    RatingListSerializer,
)
from archive.services import RatingService
from user.authentication import CustomJWTAuthentication


# Create your views here.
class RatingPageNumberPagination(PageNumberPagination):
    page_size: int = 20
    page_size_query_param: str = "page_size"
    max_page_size: int = 100

    def get_paginated_response(self, data):
        context = {
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        }

        if isinstance(data, dict):
            average_ratings = data.get("average_ratings", None)
            if average_ratings is not None:
                context["average_ratings"] = average_ratings
                context["results"] = data.get("ratings", [])

        return Response(context, status=status.HTTP_200_OK)


class RatingViewSet(ModelViewSet):
    queryset = Rating.objects
    serializer_class = RatingSerializer
    pagination_class = RatingPageNumberPagination
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [AllowAny]

    rating_service = RatingService()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.comic_id = None
        self.user_id = None

    def get_permissions(self):
        if self.action in ("create", "destroy"):
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        self.comic_id = self.request.query_params.get("comic_id")
        self.user_id = self.request.query_params.get("user_id")

        if self.comic_id and self.user_id:
            queryset = self.queryset.filter(comic=self.comic_id, user=self.user_id)
        elif self.comic_id:
            queryset = self.queryset.filter(comic=self.comic_id)
        elif self.user_id:
            queryset = self.queryset.filter(user=self.user_id)
        else:
            queryset = self.queryset.all()

        return queryset

    def get_serializer_class(self):
        serializer_classes = {
            "list": RatingRetrieveSerializer,
            "retrieve": RatingRetrieveSerializer,
        }

        if self.action == "list" and self.comic_id and not self.user_id:
            return RatingListSerializer  # 특정 만화 평점 목록

        return serializer_classes.get(self.action, RatingSerializer)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if self.comic_id and not self.user_id:
            # 평균 평점 계산
            average_rating = queryset.aggregate(Avg("rating"))["rating__avg"]
            average_rating = (
                round(float(average_rating), 1) if average_rating is not None else 0.0
            )

            response_data = {"average_ratings": average_rating}

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response_data["ratings"] = serializer.data
                return self.get_paginated_response(response_data)

            serializer = self.get_serializer(queryset, many=True)
            response_data["ratings"] = serializer.data
            return Response(response_data)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
