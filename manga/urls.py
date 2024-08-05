from django.urls import path, include

from manga.views import MangaListAPIView, index

urlpatterns = [
    path("manga/", MangaListAPIView.as_view(), name="manga-list"),
    path("index/", index, name="main_page"),
]
