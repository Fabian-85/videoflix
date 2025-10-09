from django.urls import path
from .views import VideosView

urlpatterns = [
    path('', VideosView.as_view(), name='registration'),
]
