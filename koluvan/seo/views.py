from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.db.models import Max, F, Case, When, Value, DateTimeField
from django.utils import timezone

from .helpers import get_last_template_update_date
from review.models import Review
from mebel.models import Category


class SitemapXMLTemplateView(TemplateView):
    template_name = "seo/sitemap.xml"
    content_type = "application/xml"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        # Для страницы с отзывами
        last_review = Review.objects.order_by('-date_created').only('date_created').first()
        context["date_last_review"] = last_review.date_created if last_review else now

        # Активные категории с датой последнего изменения
        context["categories"] = Category.objects.filter(
            is_active=True
        ).annotate(
            last_image_update=Max('additional_images__updated')
        ).annotate(
            last_modified=Case(
                When(
                    last_image_update__gt=F('updated'),
                    then=F('last_image_update')
                ),
                default=F('updated'),
                output_field=DateTimeField()
            )
        ).select_related('parent').prefetch_related('additional_images')

        # Для определения даты последнего изменения шаблона
        context["date_change_main"] = get_last_template_update_date("koluvan/main.html") or now
        context["date_change_privacy_policy"] = get_last_template_update_date("koluvan/privacy-policy.html") or now

        return context
