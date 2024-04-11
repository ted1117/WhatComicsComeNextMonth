from datetime import date, datetime, timedelta
from django.shortcuts import render
from django.conf import settings
import requests

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from silk.profiling.profiler import silk_profile

from manga.models import Manga, Publisher
from manga.serializers import MangaCreateSerializer, MangaModelSerializer, MangaSerializer
from manga.utils import is_numeric, parse_staff, calculate_next_month


# Create your views here.
class MangaListAPIView(generics.ListAPIView):
    queryset = Manga.objects.all()
    serializer_class = MangaModelSerializer


@silk_profile()
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


class MangaList(APIView):

    @silk_profile(name="manga2")
    def get(self, request, *args, **kwargs):
        get_manga()
        mangas = Manga.objects.all()
        serializer = MangaModelSerializer(instance=mangas, many=True)
        return Response(serializer.data)


# get_manga()
