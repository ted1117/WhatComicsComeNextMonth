from rest_framework import serializers

from cart.models import Cart
from comic.models import Comic
from comic.serializers import ComicModelSerializer


class CartRetrieveSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="comic.title", read_only=True)
    price = serializers.IntegerField(source="comic.price", read_only=True)
    published_at = serializers.DateField(
        source="comic.published_at", read_only=True
    )
    comic_id = serializers.IntegerField(source="comic.id", read_only=True)

    class Meta:
        model = Cart
        fields = ["title", "price", "published_at", "comic_id"]


class CartSerializer(serializers.Serializer):
    comics = ComicModelSerializer(many=True)

    def create(self, validated_data):
        user = self.context["request"].user
        comics_data = validated_data.pop("comics")

        cart_items = []

        for comic_data in comics_data:
            comic = Comic.objects.get(ea_isbn=comic_data["ea_isbn"])

            if Cart.objects.filter(user=user, comic=comic).exists():
                continue

            cart_item = Cart(
                user=user,
                comic=comic,
                comic_title=comic.title,
                comic_price=comic.price,
                comic_published_at=comic.published_at,
            )
            cart_item.save()
            cart_items.append(cart_item)

        return cart_items
