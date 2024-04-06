from django.urls import path, include

from manga.views import MangaList

urlpatterns = [
    path("manga/", MangaList.as_view(), name="manga-list"),
]
