from rest_framework import serializers

from comic.models import Comic, Publisher


class ComicModelSerializer(serializers.ModelSerializer):
    publisher = serializers.StringRelatedField()

    class Meta:
        model = Comic
        fields = "__all__"
        # exclude = ["id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["published_at"].input_formats = ["%Y-%m-%d"]


class ComicListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        comics = [Comic(**attrs) for attrs in validated_data]
        return Comic.objects.bulk_create(comics)


class ComicCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comic
        fields = "__all__"
        list_serializer_class = ComicListSerializer


class ComicRetrieveSerializer(serializers.ModelSerializer):
    publisher = serializers.StringRelatedField()

    class Meta:
        model = Comic
        fields = [
            "title",
            "series_title",
            "author",
            "published_at",
            "publisher",
            "price",
        ]


class ComicSerializer(serializers.Serializer):
    title = serializers.CharField()
    series_title = serializers.CharField()
    author = serializers.CharField(max_length=30)
    published_at = serializers.DateField()
    price = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["published_at"].input_formats = ["%Y-%m-%d"]
