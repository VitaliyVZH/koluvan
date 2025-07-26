from django.conf import settings
from django.core.mail import EmailMessage
import logging
logger = logging.getLogger(__name__)


def send_email_html(subject, body, content_subtype=None):
    """
    Отправляет HTML-письмо
    :param subject: Тема письма
    :param body: Содержимое письма (HTML или текст)
    """

    try:
        # Проверка настроек
        if not all([settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD]):
            logger.error("Настройки SMTP не заданы")
            return False

        # Создаем письмо
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.DEFAULT_FROM_EMAIL],
        )

        if content_subtype:
            email.content_subtype = content_subtype

        # Отправляем
        email.send()
        logger.info(f"Письмо отправлено: {subject}")
        return True

    except Exception as e:
        logger.error(f"Ошибка отправки письма: {str(e)}")
        # Детальная диагностика
        logger.debug(f"Настройки SMTP: "
                     f"HOST={settings.EMAIL_HOST}, "
                     f"PORT={settings.EMAIL_PORT}, "
                     f"USER={settings.EMAIL_HOST_USER}")
        return False
