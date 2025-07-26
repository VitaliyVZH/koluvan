from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Category, Image


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1
    fields = ('src', 'alt', 'order', 'image_preview')
    readonly_fields = ('image_preview',)
    ordering = ('order',)

    def image_preview(self, obj):
        """Превью миниатюры изображения"""
        if obj.thumb_webp:
            return mark_safe(f'<img src="{obj.thumb_webp.url}" width="100" height="75">')
        return "Нет изображения"

    image_preview.short_description = "Превью"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админ-панель для категорий"""

    inlines = [ImageInline]
    list_display = ('name', 'parent', 'is_active', 'order', 'image_preview', 'description')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'meta_title', 'meta_description', 'meta_keywords')
    list_filter = ('is_active', 'parent', 'created', 'updated')

    # Группировка полей на странице редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'parent', 'is_active', 'order', 'description')
        }),
        ('Изображение', {
            'fields': ('main_image', 'alt', 'image_preview')
        }),
        ('SEO оптимизация', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('image_preview', 'created', 'updated')

    def image_preview(self, obj):
        """Превью миниатюры категории"""
        if obj.thumb_webp:
            return mark_safe(f'<img src="{obj.thumb_webp.url}" width="150" height="100">')
        return "Нет изображения"

    image_preview.short_description = "Превью"

    # Автоматическая установка alt при сохранении
    def save_model(self, request, obj, form, change):
        if not obj.alt and obj.main_image:
            obj.alt = f"Изображение категории {obj.name}"
        super().save_model(request, obj, form, change)

    # Автоматическая установка alt для изображений в inline
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Image) and not instance.alt:
                instance.alt = f"Изображение {instance.category.name}"
            instance.save()
        formset.save_m2m()