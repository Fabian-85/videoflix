from rest_framework import serializers
from content.models import Video


class VideoSerializer(serializers.ModelSerializer):

    """
    Serializer for listing Videos.
    """

    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title', 'description',
                  'thumbnail_url', 'category']
