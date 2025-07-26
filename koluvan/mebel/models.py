from django.db import models
from django.utils.text import slugify
from django.core.validators import MinLengthValidator
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_image_extension(value):
    """Валидатор для проверки расширения изображений."""
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    if not any(value.name.lower().endswith(ext) for ext in valid_extensions):
        raise ValidationError(
            _('Неподдерживаемый формат изображения. Используйте JPG, PNG или WebP.')
        )


class TimeStampModel(models.Model):
    """
    Абстрактная модель для отслеживания времени создания и обновления.
    """
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата создания'
    )
    updated = models.DateTimeField(
        auto_now=True,
        db_index=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        abstract = True


class ImageProcessingMixin(models.Model):
    """
    Миксин для обработки изображений с генерацией оптимизированных версий.
    Требует реализации свойства 'image_source' в дочерних классах.
    """

    class Meta:
        abstract = True

    # Основные версии изображений (1200x800)
    image_avif = ImageSpecField(
        source='image_source',
        format='AVIF',
        options={'quality': 85},
        processors=[ResizeToFit(1200, 800)],
        cachefile_strategy='imagekit.cachefiles.strategies.JustInTime'
    )

    image_webp = ImageSpecField(
        source='image_source',
        format='WEBP',
        options={'quality': 85},
        processors=[ResizeToFit(1200, 800)],
        cachefile_strategy='imagekit.cachefiles.strategies.JustInTime'
    )

    image_jpeg = ImageSpecField(
        source='image_source',
        format='JPEG',
        options={'quality': 85},
        processors=[ResizeToFit(1200, 800)],
        cachefile_strategy='imagekit.cachefiles.strategies.JustInTime'
    )

    # Миниатюры (400x300)
    thumb_avif = ImageSpecField(
        source='image_source',
        format='AVIF',
        options={'quality': 70},
        processors=[ResizeToFill(400, 300)],
        cachefile_strategy='imagekit.cachefiles.strategies.JustInTime'
    )

    thumb_webp = ImageSpecField(
        source='image_source',
        format='WEBP',
        options={'quality': 70},
        processors=[ResizeToFill(400, 300)],
        cachefile_strategy='imagekit.cachefiles.strategies.JustInTime'
    )

    thumb_jpeg = ImageSpecField(
        source='image_source',
        format='JPEG',
        options={'quality': 70},
        processors=[ResizeToFill(400, 300)],
        cachefile_strategy='imagekit.cachefiles.strategies.JustInTime'
    )

    @property
    def image_source(self):
        """Должен быть переопределен в дочерних классах"""
        raise NotImplementedError("Должно быть определено поле-источник изображения")


def path_to_image(instance, filename):
    """Путь для сохранения изображений категорий с использованием slug."""
    return f'category/{instance.slug}/{filename}'


class CategoryManager(models.Manager):
    """Кастомный менеджер для категорий с оптимизированными запросами."""

    def active(self):
        """Возвращает только активные категории."""
        return self.filter(is_active=True)

    def with_prefetched_images(self):
        """Предзагружает связанные изображения."""
        return self.prefetch_related('additional_images')


class Category(TimeStampModel, ImageProcessingMixin):
    """Модель категории мебели с обработкой изображений."""
    name = models.CharField(
        max_length=50,
        verbose_name='Название категории',
        help_text='Введите название категории мебели',
        validators=[MinLengthValidator(2)]
    )

    description = models.TextField(
        blank=True,
        verbose_name='Описание категории',
        help_text='Детальное описание категории (можно использовать HTML)'
    )

    slug = models.SlugField(
        unique=True,
        max_length=60,
        db_index=True,
        verbose_name='URL-идентификатор',
        help_text='Уникальная часть URL для категории'
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
        verbose_name='Родительская категория',
        help_text='Для создания иерархии категорий'
    )

    main_image = models.ImageField(
        upload_to=path_to_image,
        verbose_name='Основное изображение',
        blank=True,
        null=True,
        validators=[validate_image_extension],
        help_text='Загрузите основное изображение категории'
    )

    alt = models.CharField(
        max_length=255,
        verbose_name='Альтернативный текст',
        help_text='Описание изображения для доступности и SEO',
        blank=True
    )

    order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name='Порядок сортировки',
        help_text='Чем выше число, тем выше в списке'
    )

    # SEO-поля
    meta_title = models.CharField(
        max_length=80,
        blank=True,
        verbose_name='SEO заголовок',
        help_text='Заголовок для SEO (макс. 80 символов)'
    )

    meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name='SEO описание',
        help_text='Описание для SEO (макс. 160 символов)'
    )

    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="SEO ключевые слова",
        help_text="Ключевые слова через запятую (макс. 255 символов)"
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name='Активна',
        help_text='Отображать категорию на сайте'
    )

    objects = CategoryManager()

    class Meta:
        db_table = 'categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['-order', 'name']
        indexes = [
            models.Index(fields=['name', 'is_active']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Автогенерация slug и alt-текста при сохранении."""
        if not self.slug:
            self.slug = slugify(self.name)[:50]

        if not self.alt and self.main_image:
            self.alt = f"Изображение категории {self.name}"

        super().save(*args, **kwargs)

    @property
    def image_source(self):
        """Реализация свойства для ImageProcessingMixin."""
        return self.main_image


class ImageManager(models.Manager):
    """Кастомный менеджер для изображений."""

    def for_category(self, category_slug):
        """Изображения для конкретной категории."""
        return self.filter(category__slug=category_slug)


def additional_image_path(instance, filename):
    """Путь для дополнительных изображений категорий."""
    return f'category/{instance.category.slug}/additional/{filename}'


class Image(TimeStampModel, ImageProcessingMixin):
    """Дополнительные изображения для категорий."""
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='additional_images',
        verbose_name='Категория',
        help_text='Выберите категорию для изображения'
    )

    src = models.ImageField(
        upload_to=additional_image_path,
        verbose_name='Изображение',
        validators=[validate_image_extension],
        help_text='Загрузите дополнительное изображение'
    )

    alt = models.CharField(
        max_length=255,
        verbose_name='Альтернативный текст',
        help_text='Описание изображения для доступности и SEO',
        blank=True
    )

    order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name='Порядок сортировки',
        help_text='Порядок отображения (меньше = раньше)'
    )

    objects = ImageManager()

    class Meta:
        db_table = 'category_images'
        verbose_name = 'Изображение категории'
        verbose_name_plural = 'Изображения категорий'
        ordering = ['order', 'created']
        indexes = [
            models.Index(fields=['category', 'order']),
        ]

    def __str__(self):
        return f"Изображение #{self.pk} для {self.category.name}"

    def save(self, *args, **kwargs):
        """Автогенерация alt-текста при сохранении."""
        if not self.alt:
            self.alt = f"Изображение {self.category.name}"
        super().save(*args, **kwargs)

    @property
    def image_source(self):
        """Реализация свойства для ImageProcessingMixin."""
        return self.src