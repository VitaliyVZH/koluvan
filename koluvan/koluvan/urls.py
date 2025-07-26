from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from mebel.views import custom_404

handler404 = custom_404

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reviews/', include('review.urls')),
    path('', include('seo.urls')),
    path('', include('mebel.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.IMAGES_URL, document_root=settings.IMAGES_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
