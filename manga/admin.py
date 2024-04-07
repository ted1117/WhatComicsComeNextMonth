from django.contrib import admin
from .models import Manga, Publisher


# Register your models here.
class MangaAdmin(admin.ModelAdmin):
    search_fields = ["title"]


admin.site.register(Manga, MangaAdmin)
admin.site.register(Publisher)
