# Generated by Django 3.2.3 on 2024-07-25 19:39

from django.db import migrations
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20240726_0216'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', users.models.UserManager()),
            ],
        ),
    ]
