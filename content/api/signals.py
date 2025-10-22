import os
import tempfile
import subprocess
import shutil
import django_rq
from pathlib import Path
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from content.models import Video


def convert_to_hdx(source, target, resolution):
    cmd = f'ffmpeg -i "{source}" -s {resolution} -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    run = subprocess.run(cmd, capture_output=True, shell=True)


def hsl_test(source, target):
    out_dir = os.path.dirname(target)
    os.makedirs(out_dir, exist_ok=True)
    cmd = 'ffmpeg -i "{}" -codec: copy -start_number 0 -hls_time 10 -hls_list_size 0 -hls_flags independent_segments -hls_segment_filename "seg_%03d.ts" -f hls "{}"'.format(
        source, target)
    run = subprocess.run(cmd, capture_output=True, cwd=out_dir, shell=True)


def helper_method(video_id, resolution):
    video = Video.objects.get(pk=video_id)
    src_path = video.video_file.path
    stem = Path(src_path).stem
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, f"{stem}_{resolution}p.mp4")
        convert_to_hdx(src_path, out, f"hd{resolution}")

        hls_dir = os.path.join(settings.MEDIA_ROOT, 'hls',
                               f'video_{video.id}', f'{resolution}p', f"{stem}_{resolution}p.m3u8")
        hsl_test(out, hls_dir)

        rel = os.path.relpath(hls_dir, settings.MEDIA_ROOT)
        field_name = f'hls_{resolution}p'
        setattr(video, field_name, rel)
        video.save(update_fields=[field_name])


@receiver(post_save, sender=Video)
def create_video(sender, instance, created, **kwargs):
    if created:
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(helper_method, instance.pk, '480')
        queue.enqueue(helper_method, instance.pk, '720')
        queue.enqueue(helper_method, instance.pk, '1080')

        #helper_method(instance.pk,  '480')
        #helper_method(instance.pk,  '720')
        #helper_method(instance.pk,'1080')


def delete_file(url):
    if url:
        if os.path.isfile(url.path):
            os.remove(url.path)


@receiver(post_delete, sender=Video)
def delete_video(sender, instance, **kwargs):
    delete_file(instance.thumbnail_url)
    delete_file(instance.video_file)
    hls_video_dir = os.path.join(
        settings.MEDIA_ROOT, 'hls', f'video_{instance.id}')
    if os.path.isdir(hls_video_dir):
        shutil.rmtree(hls_video_dir)
