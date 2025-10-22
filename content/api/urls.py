from django.urls import path
from .views import VideosView, HSLView, SegmentView

urlpatterns = [
    path('', VideosView.as_view(), name='registration'),
    path('<int:pk>/<str:resolution>/index.m3u8', HSLView.as_view()),
    path('<int:pk>/<str:resolution>/<str:segment>/', SegmentView.as_view()),
]
