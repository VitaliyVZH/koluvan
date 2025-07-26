import time
import logging

from django.views.generic import ListView
from django.urls import reverse_lazy
from django.templatetags.static import static
from django.urls import reverse
import json
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import redirect
from .models import Review
from utils.email import send_email_html
from utils.telegram import send_to_saved_messages

logger = logging.getLogger(__name__)


class ReviewListView(ListView):
    """Отзывы."""
    model = Review
    template_name = 'review/reviews.html'
    context_object_name = 'reviews'
    success_url = reverse_lazy('review:review')

    def get(self, request, *args, **kwargs):
        # Устанавливаем время начала заполнения формы, как пользователь попадает на страницу с отзывами,
        # запускается таймер и после отправки формы отзыва измеряется время с момента попадания на страницу
        # до момента отправки формы (боты это делают очень быстро)
        request.session['form_start_time'] = time.time()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Review.objects.filter(approved=True).order_by('-date_created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reviews = self.get_queryset()

        # Даты первого и последнего отзыва
        first_review = reviews.order_by('date_created').first()
        last_review = reviews.order_by('-date_created').first()

        context['date_first_review'] = first_review.date_created if first_review else None
        context['date_last_review'] = last_review.date_created if last_review else None

        reviews_data = [
            {
                'name': review.author,
                'content': review.content,
                'rating': review.rating,
                'date': review.date_created.isoformat(),
            }
            for review in reviews
        ]

        context['reviews_json'] = json.dumps(
            reviews_data,
            ensure_ascii=False,
            cls=DjangoJSONEncoder
        )

        context['image'] = self.request.build_absolute_uri(static('img/logo.svg'))
        context['url'] = self.request.build_absolute_uri(reverse('review:review'))
        context['title'] = 'Отзывы о компании по производству мебели Колыван и Ко'
        context['description'] = 'о компании по производству мебели Колыван и Ко...'
        context['form_data'] = self.request.session.get('form_data', {})

        context['meta'] = {
            'title': 'Отзывы о Колыван и Ко',
            'description': 'Прочитайте отзывы клиентов Колыван и Ко',
            'image': context['image'],
            'url': context['url'],
        }
        return context

    def post(self, request, *args, **kwargs):

        # Блок проверки формы на ботов
        # Проверка honeypot поля, если оно заполнено, значит форму заполнил бот
        honeypot_value = request.POST.get('website', '').strip()
        if honeypot_value:
            # Возвращаем успешный ответ, чтобы бот не заподозрил ловушку
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'}, status=200)
            return redirect(self.success_url)

        start_time = request.session.get('form_start_time', 0)
        if time.time() - start_time < 5:  # Менее 5 секунд
            return JsonResponse({'status': 'success'}, status=200)

            # Получаем значение рейтинга
            rating_value = request.POST.get('rating', '0')

            # Проверка рейтинга
            try:
                rating = int(rating_value)
            except (TypeError, ValueError):
                rating = 0

            # Если рейтинг = 0 - вероятно бот
            if rating == 0:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success'}, status=200)
                return redirect(self.success_url)

        # Всегда собираем данные из формы
        form_data = {
            'author': request.POST.get('reviews-page__from-name', ''),
            'content': request.POST.get('text', ''),
            'rating': request.POST.get('rating', 0)
        }

        # Создаем и сохраняем отзыв
        review = Review(
            author=form_data['author'],
            content=form_data['content'],
            rating=form_data['rating'],
            approved=False,
        )
        review.save()

        try:
            # Формируем ссылку для админки
            admin_url = self.request.build_absolute_uri(
                reverse("admin:review_review_change", args=[review.pk])
            )
        except Exception as e:
            logger.error(f"Ошибка формирования ссылки: {str(e)}")
            admin_url = ""

        # Текст для сообщения на email и тг
        header_text = f'Новый отзыв от {review.author}'
        body_text = (
            f'Вам поступил новый отзыв, для публикации на сайте необходимо '
            f'одобрить его в административной панели.\n\n'
            f'Информация об отзыве:\n'
            f'Имя автора: {review.author}\n'
            f'Отзыв: {review.content}\n'
            f'Оценка: {review.rating}\n\n'
            f'Ссылка на отзыв в административной панели: {admin_url}'
        )

        # Отправляем сообщение по электронной почте
        send_email_html(subject=header_text, body=body_text)

        # Отправляем сообщение в телеграмм
        message = f"{header_text}\n\n{body_text}"
        send_to_saved_messages(message)

        # Для AJAX-запросов возвращаем успешный статус
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'}, status=200)

        return redirect(self.success_url)
