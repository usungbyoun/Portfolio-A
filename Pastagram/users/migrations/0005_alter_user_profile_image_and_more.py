# Generated by Django 4.2.5 on 2024-01-31 04:20

import users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_relationship_user_following'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_image',
            field=models.ImageField(blank=True, upload_to=users.models.User.get_upload_path, verbose_name='프로필 이미지'),
        ),
        migrations.AlterField(
            model_name='user',
            name='short_description',
            field=models.TextField(blank=True, null=True, verbose_name='소개글'),
        ),
    ]