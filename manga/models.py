from django.db import models

# Create your models here.
class Manga(models.Model):
    title = models.CharField(max_length=50)
    series_title = models.CharField(max_length=50)
    author = models.CharField(max_length=30)
    published_at = models.DateField()
    price = models.IntegerField()