from django.urls import path
from django.views.generic import TemplateView
from .views import SitemapXMLTemplateView

app_name = 'seo'

urlpatterns = [
    path('robots.txt/', TemplateView.as_view(template_name='seo/robots.txt', content_type='text/plain')),
    path('sitemap.xml/', SitemapXMLTemplateView.as_view())
]
