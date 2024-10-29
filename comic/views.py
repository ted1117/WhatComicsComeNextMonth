from django.shortcuts import render

from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend

from comic.models import Comic
from comic.serializers import ComicModelSerializer
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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["publisher", "isSet"]
    search_fields = ["title", "author"]


def index(request):
    return render(request, "index.html", context={})
