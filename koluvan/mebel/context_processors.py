"""Кастомные контекстные процессоры."""
from .models import Category


def categories(request):
    """Возвращает категории предосталяемой продукции."""
    categories_all = Category.objects.all()
    return {'categories': categories_all}
