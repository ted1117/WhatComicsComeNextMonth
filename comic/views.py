import calendar
import datetime

from django.db.models import Q
from django.shortcuts import render

from rest_framework import generics, filters
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend

from comic.models import Comic
from comic.serializers import ComicModelSerializer, ComicRetrieveSerializer
from comic.services import ComicService


# Create your views here.
class ComicPageNumberPagination(PageNumberPagination):
    page_size: int = 20
    page_size_query_param: str = "page_size"
    max_page_size: int = 100


class ComicListAPIView(generics.ListAPIView):
    queryset = Comic.objects.all().order_by("published_at")
    serializer_class = ComicModelSerializer
    pagination_class = ComicPageNumberPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ["publisher", "isSet"]
    search_fields = ["title", "author"]

    def get_queryset(self):
        today = datetime.date.today()
        current_day = today.day
        current_year = today.year
        current_month = today.month

        last_day_of_month = calendar.monthrange(current_year, current_month)[1]

        base_queryset = Comic.objects

        if 7 <= current_day <= last_day_of_month:
            next_month_year = current_year
            next_month_month = current_month + 1
            if next_month_month > 12:
                next_month_month = 1
                next_month_year += 1

            queryset = base_queryset.filter(
                published_at__year=next_month_year, published_at__month=next_month_month
            )
        else:
            queryset = base_queryset.all()

        return queryset.order_by("published_at")


class ComicRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Comic.objects.all()
    serializer_class = ComicRetrieveSerializer


class CustomSearchFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        query = request.query_params.get("search", None)
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(author__icontains=query)
            )
        return queryset


class ComicSearchView(generics.ListAPIView):
    queryset = Comic.objects.all()
    serializer_class = ComicModelSerializer
    filter_backends = [CustomSearchFilter]
    search_fields = ["title", "author"]


def index(request):
    return render(request, "index.html", context={})
