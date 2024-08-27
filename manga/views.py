from django.shortcuts import render

from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend

from manga.models import Manga
from manga.serializers import MangaModelSerializer
from manga.services import ComicService


# Create your views here.
class MangaPageNumberPagination(PageNumberPagination):
    page_size: int = 20
    page_size_query_param: str = "page_size"
    max_page_size: int = 100


class MangaListAPIView(generics.ListAPIView):
    queryset = Manga.objects.all().order_by("published_at")
    serializer_class = MangaModelSerializer
    pagination_class = MangaPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["publisher", "isSet"]
    search_fields = ["title", "author"]


def index(request):
    return render(request, "index.html", context={})
