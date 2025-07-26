from django.conf import settings
from django.urls import path, re_path

from django.views.static import serve
from .views import MainView, CategoryDetailView, PrivacyPolicyTemplateView

app_name = 'mebel'

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('privacy_policy/', PrivacyPolicyTemplateView.as_view(), name='privacy_policy'),
    path('<str:slug>/', CategoryDetailView.as_view(), name='category_detail'),
]

urlpatterns += [
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]