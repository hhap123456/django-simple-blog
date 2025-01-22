# Generated by Django 5.1.4 on 2024-12-19 15:51

import blog.models
import django_resized.forms
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_alter_image_image_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image_file',
            field=django_resized.forms.ResizedImageField(crop=['middle', 'center'], force_format=None, keep_meta=True, quality=100, scale=None, size=[640, 360], upload_to=blog.models.upload_to_monthly),
        ),
    ]