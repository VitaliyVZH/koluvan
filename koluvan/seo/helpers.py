"""Модуль разработан для формирования данных в файле sitemap.xml."""

import os
from datetime import datetime

from django.template import TemplateDoesNotExist
from django.template.loader import get_template


def get_last_template_update_date(template_name: str) -> datetime | str:
    """Возвращает последнюю дату изменения структуры шаблона."""

    try:
        # Получаем объект шаблона.
        full_path_template = get_template(template_name)

        # Полный путь к шаблону.
        template_path = full_path_template.origin.name

        # Последняя дата изменения структуры шаблона.
        last_template_update_date = datetime.fromtimestamp(os.path.getmtime(template_path))
        return last_template_update_date

    except TemplateDoesNotExist:
        pass
