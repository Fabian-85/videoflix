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

    """
    Model representing a video with multiple HLS variants.
    Represents a video with metadata, original file, and HLS variant files.

    Fields:
    - title: Title of the video.    
    - description: Description of the video.
    - category: Category of the video (e.x. drama, action, comedy).
    - thumbnail_url: URL to the thumbnail image file.
    - created_at: Timestamp when the video was created.
    - video_file: Original uploaded video file.
    - hls_480p: HLS variant file for 480p resolution.
    - hls_720p: HLS variant file for 720p resolution.
    - hls_1080p: HLS variant file for 1080p resolution.
    """

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(choices=VIDEO_CATEGORY_CHOICES)
    thumbnail_url = models.FileField(upload_to='thumbnails/', validators=[FileExtensionValidator(allowed_extensions=IMAGE_EXTS)])
    created_at = models.DateTimeField(auto_now_add=True)
    video_file = models.FileField(upload_to='videos/',  validators=[FileExtensionValidator(allowed_extensions=VIDEO_EXTS)])
    hls_480p = models.FileField(upload_to='hls/',  null=True, blank=True,editable=False)
    hls_720p = models.FileField(upload_to='hls/',  null=True, blank=True,editable=False)
    hls_1080p = models.FileField(upload_to='hls/',  null=True, blank=True,editable=False)
    is_change_video_file = models.BooleanField(default=False, editable=False)
    
