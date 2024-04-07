from rest_framework import serializers

from manga.models import Manga, Publisher


class MangaModelSerializer(serializers.ModelSerializer):
    # publisher = serializers.CharField(source="publisher.name")
    publisher = serializers.StringRelatedField()

    class Meta:
        model = Manga
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["published_at"].input_formats = ["%Y-%m-%d"]


class MangaSerializer(serializers.Serializer):
    title = serializers.CharField()
    series_title = serializers.CharField()
    author = serializers.CharField(max_length=30)
    published_at = serializers.DateField()
    price = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["published_at"].input_formats = ["%Y-%m-%d"]
