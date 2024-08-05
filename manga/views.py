import asyncio
from datetime import date, datetime, timedelta
import aiohttp
from django.shortcuts import render
from django.conf import settings
from drfasyncview import AsyncAPIView
import requests

from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend

from silk.profiling.profiler import silk_profile

from manga.models import Manga, Publisher
from manga.serializers import MangaCreateSerializer, MangaModelSerializer, MangaSerializer
from manga.utils import is_numeric, is_set, parse_staff, calculate_next_month


# Create your views here.
async def fetch_data(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Error: {response.status}")
            return None


async def manga_to_db(session, publisher, existing_isbns):
    url = f"https://www.nl.go.kr/seoji/SearchApi.do?"

    API_KEY = settings.API_KEY
    result_style = "json"
    page_no = 1
    page_size = 200
    title = ""
    start_publish_date, end_publish_date = calculate_next_month()
    # start_publish_date, end_publish_date = "20240401", "20240430"

    params = {
        "cert_key": API_KEY,
        "result_style": result_style,
        "page_no": page_no,
        "page_size": page_size,
        "ebook_yn": "Y",
        "title": title,
        "start_publish_date": start_publish_date,
        "end_publish_date": end_publish_date,
        "publisher": publisher.search_keyword,
    }
    selected_data = []
    request_url = url + "&".join([f"{key}={value}" for key, value in params.items() if value])
    data = await fetch_data(session, request_url)

    if data:
        for manga in data["docs"]:
            if manga["EA_ISBN"] not in existing_isbns:
                if is_numeric(price := manga["PRE_PRICE"]) and manga["EA_ADD_CODE"] == publisher.ea_add_code:
                    author, illustrator, original_author, translator = parse_staff(manga["AUTHOR"])
                    manga_data = {
                        "title": manga["TITLE"],
                        "series_title": manga["SERIES_TITLE"],
                        "isSet": is_set(manga["TITLE"]),
                        "author": author,
                        "illustrator": illustrator,
                        "original_author": original_author,
                        "translator": translator,
                        "publisher": publisher.pk,
                        "published_at": datetime.strptime(manga["PUBLISH_PREDATE"], "%Y%m%d").date(),
                        "ea_isbn": manga["EA_ISBN"],
                        "price": int(price),
                    }
                    selected_data.append(manga_data)

        serializer = MangaCreateSerializer(data=selected_data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.validated_data


async def get_manga():
    publishers = Publisher.objects.all()
    existing_isbns = set(Manga.objects.values_list("ea_isbn", flat=True))

    async with aiohttp.ClientSession() as session:
        tasks = [manga_to_db(session, publisher, existing_isbns) for publisher in publishers]
        await asyncio.gather(*tasks)


@silk_profile()
def get_manga1():
    url = f"https://www.nl.go.kr/seoji/SearchApi.do?"

    API_KEY = settings.API_KEY
    result_style = "json"
    page_no = 1
    page_size = 200
    title = ""
    start_publish_date, end_publish_date = calculate_next_month()
    # start_publish_date, end_publish_date = "20240401", "20240430"
    publisher_list = [x for x in Publisher.objects.all()]

    params = {
        "cert_key": API_KEY,
        "result_style": result_style,
        "page_no": page_no,
        "page_size": page_size,
        "ebook_yn": "Y",
        "title": title,
        "start_publish_date": start_publish_date,
        "end_publish_date": end_publish_date,
        "publisher": None,
    }
    selected_data = []
    existing_isbns = set(Manga.objects.values_list("ea_isbn", flat=True))
    for publisher in publisher_list:
        params["publisher"] = publisher.search_keyword
        request_url = url + "&".join([f"{key}={value}" for key, value in params.items() if value])
        try:
            response = requests.get(request_url)
            if response.status_code == 200:
                data = response.json()

                for manga in data["docs"]:
                    if manga["EA_ISBN"] not in existing_isbns:
                        if is_numeric(price := manga["PRE_PRICE"]) and manga["EA_ADD_CODE"] == publisher.ea_add_code:
                            author, illustrator, original_author, translator = parse_staff(manga["AUTHOR"])
                            manga_data = {
                                "title": manga["TITLE"],
                                "series_title": manga["SERIES_TITLE"],
                                "isSet": is_set(manga["TITLE"]),
                                "author": author,
                                "illustrator": illustrator,
                                "original_author": original_author,
                                "translator": translator,
                                "publisher": publisher.pk,
                                "published_at": datetime.strptime(manga["PUBLISH_PREDATE"], "%Y%m%d").date(),
                                "ea_isbn": manga["EA_ISBN"],
                                "price": int(price),
                            }
                            selected_data.append(manga_data)

            else:
                print(f"Error: {response.status_code}")
        except Exception as e:
            print(f"Exception: {str(e)}")
            return None

    # 역직렬화
    serializer = MangaCreateSerializer(data=selected_data, many=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.validated_data


class MangaPageNumberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class MangaListAPIView(generics.ListAPIView):
    get_manga1()
    queryset = Manga.objects.all().order_by("published_at")
    serializer_class = MangaModelSerializer
    pagination_class = MangaPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["publisher", "isSet"]
    search_fields = ["title", "author"]


def index(request):
    return render(request, "index.html", context={})


# get_manga()
