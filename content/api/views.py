from pathlib import Path
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse,FileResponse
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from content.models import Video
from .serializers import VideoSerializer


class VideosView(generics.ListAPIView):

    """
    API view to retrieve list of Videos
    """

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes=[AllowAny]


class HSLView(APIView):

    """
    API view to retrieve HLS playlist for a video at a specific resolution

    - GET:
        Retrieves the HLS playlist (.m3u8) for the specified video and resolution.
        resolution can only be one of '480p', '720p', '1080p'.
        Permission: Only authenticated users can access.
    """
    
    permission_classes=[IsAuthenticated]

    def get(self, request, pk, resolution):
        video = get_object_or_404(Video, pk=pk)
        field = {'480p': 'hls_480p', '720p': 'hls_720p','1080p': 'hls_1080p'}.get(resolution)
        if not field:
            return Response({'detail': 'Unsupported resolution'}, status=status.HTTP_404_NOT_FOUND)
        
         
        playlist = getattr(video, field, None)
        if not playlist:
            return Response('Manifest not available', status=status.HTTP_404_NOT_FOUND)
        
        with playlist.open('rb') as fh:
            content = fh.read()

        resp = HttpResponse(content, content_type='application/vnd.apple.mpegurl')
        resp['Content-Disposition'] = 'inline; filename="index.m3u8"'
        resp['Cache-Control'] = 'public, max-age=60'
        return resp

class SegmentView(APIView):

    """
    API view to retrieve HLS segment from a video at a specific resolution

    - GET:
        Retrieves the HLS segment (.ts) from the specified video, resolution, and segment name.
        resolution can only be one of '480p', '720p', '1080p'.
        segment (str): Segment file name (e.g., 'seg_001.ts').
        Permission: Only authenticated users can access.
    """

    permission_classes=[IsAuthenticated]

    def get(self, request, pk, resolution, segment):
        video = get_object_or_404(Video, pk=pk)
        if resolution not in ('480p', '720p','1080p'):
            return Response({'detail': 'Unsupported resolution'}, status=status.HTTP_404_NOT_FOUND)
        
         
        base = Path(settings.MEDIA_ROOT) / "hls" / f"video_{pk}" / resolution
        target = (base / segment).resolve()

        if not target.exists() or not target.is_file():
            return Response('Segment not found', status=status.HTTP_404_NOT_FOUND)

        resp = FileResponse(open(target, 'rb'), content_type='video/MP2T')
        resp['Content-Disposition'] = f'inline; filename="{segment}"'
        resp['Cache-Control'] = 'public, max-age=300'
        return resp