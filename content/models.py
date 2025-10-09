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
    
