from rest_framework import serializers

from archive.models import Rating
from comic.serializers import ComicSerializer
from user.serializers import UserSerializer


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["comic", "user", "rating", "comment"]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["user"] = instance.user.nickname
        data["comic"] = instance.comic.title

        return data


class RatingRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["comic", "rating", "comment"]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["user_id"] = instance.user.id
        data["user_nickname"] = instance.user.nickname
        data["comic"] = instance.comic.title
        data["comic_id"] = instance.comic.id

        return data
