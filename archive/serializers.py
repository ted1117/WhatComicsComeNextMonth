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
    comic = ComicSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = ["comic", "user", "rating", "comment"]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["user"] = instance.user.nickname
        data["comic"] = instance.comic.title

        return data
