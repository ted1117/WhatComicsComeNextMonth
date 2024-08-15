from django.db import models

from manga.models import Manga
from user.models import CustomUser


# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comic = models.ForeignKey(Manga, on_delete=models.CASCADE)
    comic_title = models.CharField(max_length=50)
    comic_price = models.IntegerField()
    comic_published_at = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.comic_title = self.comic.title
        self.comic_price = self.comic.price
        self.comic_published_at = self.comic.published_at

        super().save(*args, **kwargs)
