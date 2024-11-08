# Generated by Django 3.2 on 2024-10-13 21:35

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reviews', '0004_profile_biography'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='favorites',
            field=models.ManyToManyField(blank=True, related_name='favorited_by', to=settings.AUTH_USER_MODEL),
        ),
    ]