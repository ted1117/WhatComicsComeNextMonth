from django.urls import path, include

from rest_framework.routers import DefaultRouter

from archive.views import RatingViewSet

router = DefaultRouter()
router.register(r"", RatingViewSet, basename="archive")

urlpatterns = [
    path("", include(router.urls)),
]
