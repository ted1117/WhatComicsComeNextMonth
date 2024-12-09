from rest_framework.exceptions import NotFound
from decimal import Decimal
from django.db import transaction
from django.db.models import Q

from archive.models import Rating
from comic.models import Comic
from user.models import CustomUser


class RatingService:
    @transaction.atomic
    def create_rating(
        self,
        comic_id: int,
        user: CustomUser,
        rating: Decimal = None,
        comment: str = None,
    ):
        try:
            comic = Comic.objects.get(id=comic_id)
        except Comic.DoesNotExist:
            raise NotFound({"error": f"Comic with id {comic_id} does not exist."})

        rating = Rating.objects.create(
            user=user, comic=comic, rating=rating, comment=comment
        )

        return rating
