import django_rq
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete
from content.models import Video
from content.api.functions import build_hls_variant, delete_file_if_exists, delete_hls_directory_for_video


@receiver(post_save, sender=Video)
def enqueue_hls_jobs_on_create(sender, instance, created, **kwargs):
    if created:
        print("created")
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(build_hls_variant, instance.pk, '480')
        queue.enqueue(build_hls_variant, instance.pk, '720')
        queue.enqueue(build_hls_variant, instance.pk, '1080')
    else:
        print("updated")


@receiver(post_delete, sender=Video)
def cleanup_video_files_on_delete(sender, instance, **kwargs):
    delete_file_if_exists(instance.thumbnail_url)
    delete_file_if_exists(instance.video_file)
    delete_hls_directory_for_video(instance.id)
