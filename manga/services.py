import asyncio
from datetime import datetime
from typing import Any
import aiohttp
from django.conf import settings
from silk.profiling.profiler import silk_profile
import requests

from manga.models import Manga, Publisher
from manga.serializers import MangaCreateSerializer
from manga.utils import calculate_next_month, is_numeric, is_set, parse_staff


class ComicService:

    @staticmethod
    @silk_profile()
    def fetch_comic():
        url: str = f"https://www.nl.go.kr/seoji/SearchApi.do?"
        API_KEY: str = settings.API_KEY
        result_style: str = "json"
        page_no: int = 1
        page_size: int = 200
        title: str = ""
        start_publish_date, end_publish_date = calculate_next_month()

        publisher_list: list[Publisher] = [x for x in Publisher.objects.all()]

        params: dict[str, Any] = {
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

        selected_data: list[dict] = []
        existing_isbns: set = set(Manga.objects.values_list("ea_isbn", flat=True))

        for publisher in publisher_list:
            params["publisher"] = publisher.search_keyword
            request_url = url + "&".join([f"{key}={value}" for key, value in params.items() if value])
            try:
                response = requests.get(request_url)
                if response.status_code == 200:
                    data: dict = response.json()

                    for comic in data["docs"]:
                        if comic["EA_ISBN"] not in existing_isbns:
                            if (
                                is_numeric(price := comic["PRE_PRICE"])
                                and comic["EA_ADD_CODE"] == publisher.ea_add_code
                            ):
                                author, illustrator, original_author, translator = parse_staff(comic["AUTHOR"])
                                manga_data = {
                                    "title": comic["TITLE"],
                                    "series_title": comic["SERIES_TITLE"],
                                    "isSet": is_set(comic["TITLE"]),
                                    "author": author,
                                    "illustrator": illustrator,
                                    "original_author": original_author,
                                    "translator": translator,
                                    "publisher": publisher.pk,
                                    "published_at": datetime.strptime(comic["PUBLISH_PREDATE"], "%Y%m%d").date(),
                                    "ea_isbn": comic["EA_ISBN"],
                                    "price": int(price),
                                }
                                selected_data.append(manga_data)
                else:
                    print(f"Error: {response.status_code}")
            except Exception as e:
                print(f"Exception: {str(e)}")
                return None

        # 데이터 역직렬화 및 저장
        serializer = MangaCreateSerializer(data=selected_data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.validated_data


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
