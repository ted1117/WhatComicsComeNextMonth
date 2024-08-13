from django.db import models

from manga.models import Manga
from user.models import CustomUser


# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE)
    manga_title = models.CharField(max_length=50)
    manga_price = models.IntegerField()
    manga_published_at = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.manga_title = self.manga.title
        self.manga_price = self.manga.price
        self.manga_published_at = self.manga.published_at

        super().save(*args, **kwargs)
