from datetime import date, datetime, timedelta
from django.shortcuts import render
from django.conf import settings
import requests

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from manga.models import Manga
from manga.serializers import MangaModelSerializer

# Create your views here.
class MangaListAPIView(generics.ListAPIView):
    queryset = Manga.objects.all()
    serializer_class = MangaModelSerializer

class MangaCreateAPIView(generics.CreateAPIView):
    queryset = Manga.objects.all()
    serializer_class = MangaModelSerializer

    def perform_create(self, serializer):
        url = "https://www.nl.go.kr/seoji/SearchApi.do?"
        response = requests.get(url)

def calculate_next_month():
    today = date.today()

    next_month_first_day = datetime(today.year, today.month + 1, 1)
    next_month_last_day = datetime(today.year, today.month + 2, 1) - timedelta(days=1)

    return next_month_first_day.strftime("%Y%m%d"), next_month_last_day.strftime("%Y%m%d")


def get_manga():
    url = f"https://www.nl.go.kr/seoji/SearchApi.do?"
    API_KEY = settings.API_KEY
    # print(API_KEY)
    result_style = "json"
    # request_url = url + f"?cert_key={API_KEY}" + f"&result_style={result_style}"
    page_no = 1
    page_size = 100
    title = ""
    start_publish_date, end_publish_date = calculate_next_month()
    publisher = "디씨더블유"
    params = {
        "cert_key": API_KEY,
        "result_style": result_style,
        "page_no": page_no,
        "page_size": page_size,
        "ebook_yn": "Y",
        "title": title,
        "start_publish_date": start_publish_date,
        "end_publish_date": end_publish_date,
        "publisher": publisher,
    }
    request_url = url + "&".join([f"{key}={value}" for key, value in params.items() if value])
    try:
        response = requests.get(request_url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Exception: {str(e)}")
        return None

class MangaList(APIView):
    def get(self, request, format=None):
        data = get_manga()
        print(type(data))
        if data:
            return Response(data, status=status.HTTP_200_OK)
        return Response("Error occurred")
