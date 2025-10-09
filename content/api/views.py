from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from content.models import Video
from .serializers import VideoSerializer


class VideosView(generics.ListAPIView):

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes=[AllowAny]