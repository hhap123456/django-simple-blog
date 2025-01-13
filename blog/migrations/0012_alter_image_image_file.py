# Generated by Django 5.1.4 on 2024-12-18 21:44

import django_resized.forms
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_alter_image_options_alter_image_image_file_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image_file',
            field=django_resized.forms.ResizedImageField(crop=['middle', 'center'], force_format=None, keep_meta=True, quality=90, scale=None, size=[640, 360], upload_to='post_images'),
        ),
    ]
