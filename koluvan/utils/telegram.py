import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import logging

logger = logging.getLogger(__name__)


def send_to_saved_messages(message):
    """Отправляет сообщение в ваш раздел Saved Messages"""
    # Проверка настроек
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ImproperlyConfigured('TELEGRAM_BOT_TOKEN не настроен')
    if not settings.TELEGRAM_USER_ID:
        raise ImproperlyConfigured('TELEGRAM_USER_ID не настроен')

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_USER_ID,
        "text": message,
        "parse_mode": "HTML",  # Для форматирования
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()  # Проверка на ошибки HTTP
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка отправки в Telegram: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        return False
