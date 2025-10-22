from django.db import models


VIDEO_CATEGORY_CHOICES = {
    ('drama', 'Drama'),
    ('action', 'Action'),
    ('comedy', 'Comedy')
}

class Video(models.Model):

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(choices=VIDEO_CATEGORY_CHOICES)
    thumbnail_url = models.FileField(upload_to='thumbnails/')
    created_at = models.DateTimeField(auto_now_add=True)

    video_file = models.FileField(upload_to='videos/', null=True)

    hls_480p = models.FileField(upload_to='hls/',  null=True, blank=True,editable=False)
    hls_720p = models.FileField(upload_to='hls/',  null=True, blank=True,editable=False)
    hls_1080p = models.FileField(upload_to='hls/',  null=True, blank=True,editable=False)
    
