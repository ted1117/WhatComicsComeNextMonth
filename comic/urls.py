from django.urls import path, include

from comic.views import ComicListAPIView, index

urlpatterns = [
    path("comic/", ComicListAPIView.as_view(), name="comic-list"),
    path("index/", index, name="main_page"),
]
