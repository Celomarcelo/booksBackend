# Generated by Django 3.2 on 2024-10-17 09:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0014_auto_20241016_2158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='genre',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reviews.genre'),
        ),
    ]
