from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewsAdmin(admin.ModelAdmin):
    """Админка отзывов."""
    list_display = ('author', 'content', 'rating', 'date_created', 'approved')