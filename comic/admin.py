from django.contrib import admin

from user.models import CustomUser
from .models import Comic, Publisher


# Register your models here.
class ComicAdmin(admin.ModelAdmin):
    search_fields = ["title"]


admin.site.register(Comic, ComicAdmin)
admin.site.register(Publisher)
admin.site.register(CustomUser)
