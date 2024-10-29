from django.test import TestCase
from django.urls import reverse


from cart.models import Cart
from cart.serializers import CartRetrieveSerializer
from comic.models import Comic, Publisher
from comic.serializers import ComicCreateSerializer
from user.models import CustomUser
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


# Create your tests here.
class CartAPITestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="user1@naver.com", password="testpass"
        )
        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.comic = Comic.objects.create(
            title="Test Comic",
            series_title="Test Series",
            author="Test Author",
            illustrator="Test Illustrator",
            original_author="Original Author",
            translator="Test Translator",
            isSet=False,
            ea_isbn="1234567890",
            publisher=self.publisher,
            published_at="2023-08-15",
            price=1000,
        )
        self.cart_item = Cart.objects.create(
            user=self.user,
            comic=self.comic,
            comic_title=self.comic.title,
            comic_price=self.comic.price,
            comic_published_at=self.comic.published_at,
        )
        self.url = "/cart/"

        # JWT Token 생성
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

    def test_get_cart(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer_data = CartRetrieveSerializer(
            [self.cart_item], many=True
        ).data
        total_price = sum([comic["price"] for comic in serializer_data])

        self.assertEqual(response.data["results"]["total_price"], total_price)
        self.assertEqual(len(response.data["results"]["cart_items"]), 1)

    def test_post_cart(self):
        new_comic = Comic.objects.create(
            title="New Comic",
            series_title="New Series",
            author="New Author",
            illustrator="New Illustrator",
            original_author="Original Author",
            translator="New Translator",
            isSet=False,
            ea_isbn="0987654321",
            publisher=self.publisher,
            published_at="2023-08-16",
            price=1500,
        )
        serialized_comic = ComicCreateSerializer(new_comic).data

        comicArray = [serialized_comic]
        data = {"comics": comicArray}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 2)

    def test_delete_cart(self):
        data = {"comics": [self.cart_item.comic.id]}
        response = self.client.delete(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 0)
