from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from comic.models import Comic
from user.models import CustomUser


# Create your models here.
class Rating(models.Model):
    comic = models.ForeignKey(to=Comic, on_delete=models.CASCADE)
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        blank=True,
        default=0.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0),
        ],
    )
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = ("comic", "user")

    def clean(self):
        """점수가 0.5 단위인지 검증"""
        if float(self.rating) * 10 % 5 != 0:
            raise ValidationError("Rating must be in 0.5 increments.")
