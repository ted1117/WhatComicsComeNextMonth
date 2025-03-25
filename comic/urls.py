from django.urls import path, include

from comic.views import ComicListAPIView, ComicRetrieveAPIView, ComicSearchView, index

urlpatterns = [
    path("comic/", ComicListAPIView.as_view(), name="comic-list"),
    path("comic/<int:pk>/", ComicRetrieveAPIView.as_view()),
    path("comic/search/", ComicSearchView.as_view()),
    path("index/", index, name="main_page"),
]
