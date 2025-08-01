# Generated by Django 5.2.4 on 2025-07-06 20:11

import mebel.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mebel', '0002_alter_image_src'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='meta_keywords',
            field=models.TextField(blank=True, help_text='Ключевые слова для SEO, разделенные запятыми (макс. 255 символов)', max_length=255, null=True, verbose_name='Мета-ключевые слова'),
        ),
        migrations.AlterField(
            model_name='category',
            name='main_image',
            field=models.ImageField(blank=True, help_text='Загрузите изображение категории', null=True, upload_to=mebel.models.path_to_image, verbose_name='Изображение'),
        ),
    ]
