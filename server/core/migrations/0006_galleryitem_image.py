# Generated by Django 2.2 on 2022-01-01 03:07

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_gallery'),
    ]

    operations = [
        migrations.AddField(
            model_name='galleryitem',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.gallery_item_image_file_path),
        ),
    ]
