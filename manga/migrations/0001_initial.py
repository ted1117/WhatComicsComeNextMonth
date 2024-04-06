# Generated by Django 5.0.4 on 2024-04-04 17:43

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Manga",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=50)),
                ("series_title", models.CharField(max_length=50)),
                ("author", models.CharField(max_length=30)),
                ("published_at", models.DateField()),
                ("price", models.IntegerField()),
            ],
        ),
    ]
