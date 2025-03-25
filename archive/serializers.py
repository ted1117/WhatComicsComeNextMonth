from rest_framework import serializers

from archive.models import Rating


class RatingSerializer(serializers.ModelSerializer):
    """평점 생성·수정 시리얼라이저"""

    class Meta:
        model = Rating
        fields = ["comic", "user", "rating", "comment"]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["user"] = instance.user.nickname
        data["comic"] = instance.comic.title

        return data


class RatingRetrieveSerializer(serializers.ModelSerializer):
    """평점 상세 조회 시리얼라이저"""

    class Meta:
        model = Rating
        fields = ["comic", "rating", "comment", "created_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["user_id"] = instance.user.id
        data["user_nickname"] = instance.user.nickname
        data["comic"] = instance.comic.title
        data["comic_id"] = instance.comic.id

        return data


class RatingListSerializer(serializers.ModelSerializer):
    """평점 목록 시리얼라이저"""

    user_id = serializers.ReadOnlyField(source="user.id")
    user_nickname = serializers.ReadOnlyField(source="user.nickname")

    class Meta:
        model = Rating
        fields = ["user_id", "user_nickname", "rating", "comment", "created_at"]
