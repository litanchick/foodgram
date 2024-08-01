# Generated by Django 3.2.3 on 2024-07-30 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_alter_ingredients_name'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='listingredients',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_ingredient_recipe'),
        ),
    ]
