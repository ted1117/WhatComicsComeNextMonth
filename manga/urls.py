from django.urls import path, include

from manga.views import MangaList, MangaListAPIView, MangaTestAPIView, index

urlpatterns = [
    path("manga/", MangaListAPIView.as_view(), name="manga-list"),
    path("manga2/", MangaList.as_view(), name="manga-list2"),
    path("manga3/", MangaTestAPIView.as_view()),
    path("index/", index, name="main_page"),
]
