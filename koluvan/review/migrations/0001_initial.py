# Generated by Django 5.2.4 on 2025-07-20 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(help_text='Введите имя автора', max_length=100, verbose_name='Имя автора')),
                ('city', models.CharField(blank=True, help_text='Введите город автора', max_length=100, verbose_name='Город автора')),
                ('content', models.TextField(help_text='Напишите отзыв', verbose_name='Отзыв')),
                ('rating', models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], verbose_name='Оценка (1-5)')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('approved', models.BooleanField(default=False, verbose_name='Одобрен')),
            ],
            options={
                'verbose_name': 'отзыв',
                'verbose_name_plural': 'отзывы',
                'db_table': 'reviews',
            },
        ),
    ]
