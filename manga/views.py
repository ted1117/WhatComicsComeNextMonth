from datetime import date, datetime, timedelta
import select
from django.shortcuts import render
from django.conf import settings
import requests

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from manga.models import Manga, Publisher
from manga.serializers import MangaModelSerializer, MangaSerializer


# Create your views here.
class MangaListAPIView(generics.ListAPIView):
    queryset = Manga.objects.all()
    serializer_class = MangaModelSerializer


def calculate_next_month():
    today = date.today()

    next_month_first_day = datetime(today.year, today.month + 1, 1)
    next_month_last_day = datetime(today.year, today.month + 2, 1) - timedelta(days=1)

    return next_month_first_day.strftime("%Y%m%d"), next_month_last_day.strftime("%Y%m%d")


def get_manga():
    url = f"https://www.nl.go.kr/seoji/SearchApi.do?"

    API_KEY = settings.API_KEY
    result_style = "json"
    page_no = 1
    page_size = 200
    title = ""
    # start_publish_date, end_publish_date = calculate_next_month()
    start_publish_date, end_publish_date = "20240401", "20240430"
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
    for publisher in publisher_list:
        params["publisher"] = publisher.search_keyword
        request_url = url + "&".join([f"{key}={value}" for key, value in params.items() if value])
        print(request_url)
        try:
            response = requests.get(request_url)
            if response.status_code == 200:
                data = response.json()

                selected_data += [
                    {
                        "title": manga["TITLE"],
                        "series_title": manga["SERIES_TITLE"],
                        "author": manga["AUTHOR"],
                        "publisher": publisher.pk,
                        "published_at": datetime.strptime(manga["PUBLISH_PREDATE"], "%Y%m%d").date(),
                        "price": int(manga["PRE_PRICE"]),
                    }
                    for manga in data["docs"]
                    if not manga["PRE_PRICE"].isalpha() and manga["EA_ADD_CODE"] == publisher.ea_add_code
                ]

            else:
                print(f"Error: {response.status_code}")
        except Exception as e:
            print(f"Exception: {str(e)}")
            return None

    # 역직렬화
    serializer = MangaModelSerializer(data=selected_data, many=True)
    print(type(selected_data))
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.validated_data


class MangaList(APIView):
    def get(self, request, *args, **kwargs):
        # get_manga()
        mangas = Manga.objects.all()
        data = [
            {
                "title": manga.title,
                "series_title": manga.series_title,
                "author": manga.author,
                "publisher": manga.publisher,
                "published_at": manga.published_at,
                "price": manga.price,
            }
            for manga in mangas
        ]
        serializer = MangaModelSerializer(instance=data, many=True)
        return Response(serializer.data)


# get_manga()
