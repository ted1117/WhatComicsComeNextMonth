from rest_framework import serializers

from cart.models import Cart
from manga.models import Manga
from manga.serializers import MangaModelSerializer


class CartRetrieveSerializer(serializers.ModelSerializer):
    manga_title = serializers.CharField(source="manga.title", read_only=True)
    manga_price = serializers.IntegerField(source="manga.price", read_only=True)
    manga_published_at = serializers.DateField(source="manga.published_at", read_only=True)

    class Meta:
        model = Cart
        fields = ["manga_title", "manga_price", "manga_published_at"]


class CartSerializer(serializers.Serializer):
    comics = MangaModelSerializer(many=True)

    def create(self, validated_data):
        user = self.context["request"].user
        comics_data = validated_data.pop("comics")

        cart_items = []

        for comic_data in comics_data:
            comic = Manga.objects.get(ea_isbn=comic_data["ea_isbn"])

            if Cart.objects.filter(user=user, manga=comic).exists():
                continue

            cart_item = Cart(
                user=user,
                manga=comic,
                manga_title=comic.title,
                manga_price=comic.price,
                manga_published_at=comic.published_at,
            )
            cart_item.save()
            cart_items.append(cart_item)

        return cart_items
