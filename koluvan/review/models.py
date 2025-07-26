from django.db import models


class Review(models.Model):
    """Отзывы."""

    author = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        verbose_name='Имя автора',
        help_text='Введите имя автора'
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        null=False,
        verbose_name='Город автора',
        help_text='Введите город автора'
    )

    content = models.TextField(
        blank=False,
        null=False,
        verbose_name='Отзыв',
        help_text='Напишите отзыв'
    )
    rating = models.PositiveSmallIntegerField(
        blank=False,
        null=False,
        verbose_name="Оценка (1-5)",
        choices=[
            (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')
        ]
    )

    date_created = models.DateTimeField(
        verbose_name="Дата создания",
        auto_now_add=True
    )

    approved = models.BooleanField(
        verbose_name="Одобрен",
        default=False
    )

    class Meta:
        db_table = 'reviews'
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'

    def str(self):
        return f"{self.author} - {self.rating}/5"
