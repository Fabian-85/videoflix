from django.core.validators import FileExtensionValidator
from django.db import models


VIDEO_CATEGORY_CHOICES = {
    ('drama', 'Drama'),
    ('action', 'Action'),
    ('comedy', 'Comedy')
}

VIDEO_EXTS = ["mp4", "mov", "mkv", "webm", "avi"]
IMAGE_EXTS = ["jpg", "jpeg", "png", "gif", "webp"]
class Video(models.Model):

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(choices=VIDEO_CATEGORY_CHOICES)
    thumbnail_url = models.FileField(upload_to='thumbnails/', validators=[FileExtensionValidator(allowed_extensions=IMAGE_EXTS)])
    created_at = models.DateTimeField(auto_now_add=True)

    video_file = models.FileField(upload_to='videos/',  validators=[FileExtensionValidator(allowed_extensions=VIDEO_EXTS)], null=True)

    hls_480p = models.FileField(upload_to='hls/',  null=True, blank=True,editable=False)
    hls_720p = models.FileField(upload_to='hls/',  null=True, blank=True,editable=False)
    hls_1080p = models.FileField(upload_to='hls/',  null=True, blank=True,editable=False)
    
