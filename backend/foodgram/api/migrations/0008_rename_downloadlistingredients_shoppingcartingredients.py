# Generated by Django 3.2.3 on 2024-07-29 18:16

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0007_alter_ingredients_measurement_unit'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DownloadListIngredients',
            new_name='ShoppingCartIngredients',
        ),
    ]