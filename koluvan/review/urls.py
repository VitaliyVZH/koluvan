from django.urls import path

from .views import ReviewListView


app_name = 'review'

urlpatterns = [
    path('', ReviewListView.as_view(), name='review')
]
