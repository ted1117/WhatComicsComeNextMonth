from datetime import datetime
from typing import Any

import httpx
from celery import shared_task
from django.conf import settings
from silk.profiling.profiler import silk_profile

from comic.models import Comic, Publisher
from comic.serializers import ComicCreateSerializer
from comic.utils import calculate_next_month, is_numeric, is_set, parse_staff


class ComicService:

    @staticmethod
    @silk_profile
    @shared_task(name="comic.services.ComicService.fetch_comic")
    def fetch_comic():
        url: str = "https://www.nl.go.kr/seoji/SearchApi.do?"
        API_KEY: str = settings.API_KEY
        result_style: str = "json"
        page_no: int = 1
        page_size: int = 200
        title: str = ""
        start_publish_date, end_publish_date = calculate_next_month()

        # Publisher 데이터를 동기로 가져오기
        publisher_list: list[Publisher] = list(Publisher.objects.all())

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

        # 기존 ISBN 데이터 가져오기
        existing_isbns: set = set(Comic.objects.values_list("ea_isbn", flat=True))

        selected_data: list[dict] = []

        with httpx.Client() as client:  # 동기 클라이언트
            for publisher in publisher_list:
                params["publisher"] = publisher.search_keyword
                request_url = url + "&".join(
                    [f"{key}={value}" for key, value in params.items() if value]
                )
                try:
                    response = client.get(request_url)
                    if response.status_code == 200:
                        data: dict = response.json()

                        for comic in data.get("docs", []):
                            if comic["EA_ISBN"] not in existing_isbns:
                                if (
                                    is_numeric(price := comic.get("PRE_PRICE"))
                                    and comic["EA_ADD_CODE"] == publisher.ea_add_code
                                ):
                                    (
                                        author,
                                        illustrator,
                                        original_author,
                                        translator,
                                    ) = parse_staff(comic["AUTHOR"])
                                    comic_data = {
                                        "title": comic["TITLE"],
                                        "series_title": comic["SERIES_TITLE"],
                                        "isSet": is_set(comic["TITLE"]),
                                        "author": author,
                                        "illustrator": illustrator,
                                        "original_author": original_author,
                                        "translator": translator,
                                        "publisher": publisher.pk,
                                        "published_at": datetime.strptime(
                                            comic["PUBLISH_PREDATE"], "%Y%m%d"
                                        ).date(),
                                        "ea_isbn": comic["EA_ISBN"],
                                        "price": int(price),
                                    }
                                    selected_data.append(comic_data)
                    else:
                        print(f"Error: {response.status_code}")
                except httpx.RequestError as e:
                    print(f"Request failed: {e}")
                    return None

        # 데이터 역직렬화 및 저장
        serializer = ComicCreateSerializer(data=selected_data, many=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        print("end!")
        return serializer.validated_data
