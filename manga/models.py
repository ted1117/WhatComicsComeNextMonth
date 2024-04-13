from typing import Iterable
from django.db import models


# Create your models here.
class Publisher(models.Model):
    name = models.CharField(max_length=50)
    ea_add_code = models.CharField(max_length=6, default="05830")
    subject = models.IntegerField(default=8)
    search_keyword = models.CharField(max_length=50, blank=True)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.search_keyword:
            self.search_keyword = self.name
        super().save(*args, **kwargs)


class Manga(models.Model):
    title = models.CharField(max_length=150)
    series_title = models.CharField(max_length=150, blank=True)
    author = models.CharField(max_length=300)
    illustrator = models.CharField(max_length=100, null=True)
    original_author = models.CharField(max_length=100, null=True)
    translator = models.CharField(max_length=100, null=True)
    isSet = models.BooleanField(default=False)
    ea_isbn = models.CharField(max_length=50, blank=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.DO_NOTHING)
    published_at = models.DateField()
    price = models.IntegerField()

    def __str__(self) -> str:
        return self.title
