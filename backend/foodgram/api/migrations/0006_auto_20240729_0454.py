# Generated by Django 3.2.3 on 2024-07-28 21:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_remove_recipes_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listingredients',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipeingredient', to='api.ingredients', verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='listingredients',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipeingredient', to='api.recipes', verbose_name='Рецепт'),
        ),
    ]
