import logging
import time

from django.urls import reverse
from django.templatetags.static import static

from .forms import RequestCallBackForm
from django.urls import reverse_lazy
from django.views.generic import FormView, DetailView,TemplateView
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.html import escape
from .models import Category
from utils.email import send_email_html
from utils.telegram import send_to_saved_messages

logger = logging.getLogger(__name__)


def custom_404(request, exception):
    try:
        return render(request, 'koluvan/404.html', status=404)
    except Exception as e:
        # Логирование ошибки
        logger.error(f"Ошибка при рендеринге 404: {e}")
        # Возвращаем простой текст в случае ошибки
        return HttpResponse("Страница не найдена", status=404)


class MainView(FormView):
    """Главная страница."""

    template_name = 'koluvan/main.html'
    form_class = RequestCallBackForm
    success_url = reverse_lazy('mebel:main')

    def get(self, request, *args, **kwargs):
        # Устанавливаем время начала заполнения формы, как пользователь попадает на страницу с отзывами,
        # запускается таймер и после отправки формы отзыва измеряется время с момента попадания на страницу
        # до момента отправки формы (боты это делают очень быстро)
        request.session['form_start_time'] = time.time()
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        # Извлекаем и обрабатываем данные
        name = escape(form.cleaned_data['name'].title())
        phone = escape(form.cleaned_data['phone'])
        category = escape(form.cleaned_data.get('category', ''))
        raw_message = form.cleaned_data.get('message', '')
        website = form.cleaned_data.get('website', '')

        if website:
            return super().form_valid(form)

        start_time = self.request.session.get('form_start_time', 0)
        if time.time() - start_time < 5:  # Менее 5 секунд
            return super().form_valid(form)

        # Обрабатываем сообщение с сохранением переносов
        message_html = ''
        if raw_message:
            escaped_message = escape(raw_message)
            message_html = f"""
            <div class="info optional">
                <h3>Сообщение от клиента:</h3>
                <p>{escaped_message}</p>
            </div>
            """

        # Формируем HTML-письмо
        email_body = f"""
        <html>
        <head>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    color: #333;
                    line-height: 1.6;
                    background-color: #f9f9f9;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 15px;
                    margin-bottom: 20px;
                }}
                .info {{ 
                    margin: 20px 0;
                    padding: 15px;
                    border-left: 4px solid #3498db;
                    background-color: #f8fafc;
                }}
                .optional {{
                    background-color: #f1f8ff;
                    border-left-color: #1e6bd0;
                }}
                .label {{
                    font-weight: bold;
                    color: #1e6bd0;
                    min-width: 120px;
                    display: inline-block;
                }}
                .contact-info {{
                    background-color: #e3f2fd;
                    padding: 15px;
                    border-radius: 8px;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #7f8c8d;
                    font-size: 0.9em;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>📞 Заявка на обратный звонок</h2>
                </div>

                <div class="contact-info">
                    <div class="info">
                        <p><span class="label">Имя клиента:</span> {name}</p>
                        <p><span class="label">Телефон:</span> 
                            <a href="tel:{phone}" style="color: #0d47a1; text-decoration: none;">
                                <strong>{phone}</strong>
                            </a>
                        </p>
                    </div>
        """

        # Добавляем категорию если есть
        if category:
            email_body += f"""
                    <div class="info optional">
                        <p><span class="label">Категория:</span> {category}</p>
                    </div>
            """

        email_body += f"""
                </div>
                {message_html}

                <div class="footer">
                    <p>🕒 Рекомендуемое время звонка: <b>в течение 15 минут</b></p>
                    <p>✉️ Это автоматическое сообщение, пожалуйста не отвечайте на него</p>
                </div>
            </div>
        </body>
        </html>
        """

        header_text = f"Заявка на обратный звонок от {name}"
        send_email_html(subject=header_text, body=email_body, content_subtype='html')

        # Отправляем сообщение в телеграмм
        message = (f"{header_text}\n\n"
                   f"Имя клиента: {name}\n"
                   f"Телефон клиента: {phone}\n"
                   f"Категория продукции: {category}\n"
                   f"Сообщение клиента: {raw_message}")
        send_to_saved_messages(message)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        title = 'Мебель на заказ в Мариуполе | Изготовление корпусной мебели'
        description = 'Изготовление корпусной мебели на заказ в Мариуполе. Кухни, шкафы, тумбы по индивидуальным размерам. Бесплатный замер, качественные материалы, гарантия.'
        keywords = 'мебель на заказ мариуполь, корпусная мебель, кухни на заказ, шкафы купе, тумбочки на заказ, мебель под заказ, изготовление мебели мариуполь, гарнитуры на заказ, встроенная мебель'
        image = self.request.build_absolute_uri(static('img/logo.svg'))

        context['url'] = self.request.build_absolute_uri(reverse('mebel:main'))

        context['title'] = 'Мебель на заказ в Мариуполе | В оговоренные сроки'
        context['description'] = 'Бесплатный замер и проект! Изготовление кухонь, шкафов и тумб по индивидуальным размерам. ⭐ 500+ довольных клиентов в Мариуполе'
        context['keywords'] = keywords

        context['image'] = image

        # Инициализируем мета-теги (meta name).
        context['meta'] = {
            'title': title,
            'description': description,
            'keywords': keywords,
            'image': image,
        }
        return context


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'koluvan/category-detail.html'
    context_object_name = 'category'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object

        # Получаем все дополнительные изображения для этой категории
        additional_images = category.additional_images.all()
        context['additional_images'] = additional_images

        # Мета-теги для SEO
        context['meta'] = {
            'title': category.meta_title if category.meta_title else f"{category.name} | Мебель на заказ в Мариуполе",
            'description': category.meta_description if category.meta_description else f"Примеры работ по категории {category.name}. Изготовление мебели на заказ в Мариуполе.",
            'keywords': category.meta_keywords if category.meta_keywords else f"мебель на заказ мариуполь, {category.name.lower()}, примеры работ, фото",
            'image': self.request.build_absolute_uri(category.main_image.url) if category.main_image else None,
        }
        return context


class PrivacyPolicyTemplateView(TemplateView):
    template_name = 'koluvan/privacy-policy.html'
