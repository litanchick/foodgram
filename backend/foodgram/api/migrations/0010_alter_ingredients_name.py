# Generated by Django 3.2.3 on 2024-07-30 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_alter_recipes_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredients',
            name='name',
            field=models.CharField(max_length=128, unique=True, verbose_name='Название ингредиента'),
        ),
    ]