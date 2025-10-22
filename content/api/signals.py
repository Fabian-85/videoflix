import os, tempfile
import subprocess
import shutil
from pathlib import Path
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from content.models import Video


def convert_to_hdx(source, target, resolution):
    cmd = f'ffmpeg -i "{source}" -s {resolution} -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    run = subprocess.run(cmd, capture_output=True,shell=True)


def hsl_test(source, target): 
    out_dir = os.path.dirname(target)
    os.makedirs(out_dir, exist_ok=True)
    cmd = 'ffmpeg -i "{}" -codec: copy -start_number 0 -hls_time 10 -hls_list_size 0 -hls_flags independent_segments -hls_segment_filename "seg_%03d.ts" -f hls "{}"'.format(source, target) 
    run = subprocess.run(cmd, capture_output=True, cwd=out_dir,shell=True)


@receiver(post_save, sender=Video)
def create_video(sender, instance, created, **kwargs):
    if created:
        video_id = instance.pk
        video = Video.objects.get(pk=video_id)
        src_path = video.video_file.path
        stem = Path(src_path).stem

        with tempfile.TemporaryDirectory() as tmp:
            out480 = os.path.join(tmp, f"{stem}_480p.mp4")
            out720 = os.path.join(tmp, f"{stem}_720p.mp4")
            out1080 = os.path.join(tmp, f"{stem}_1080p.mp4")

            convert_to_hdx(src_path, out480, 'hd480')
            convert_to_hdx(src_path, out720,'hd720')
            convert_to_hdx(src_path, out1080,'hd1080')

            

            hls_dir_480 = os.path.join(settings.MEDIA_ROOT, 'hls', f'video_{video.id}', '480p', f"{stem}_480p.m3u8")
            hsl_test(out480,hls_dir_480)

            hls_dir_720 = os.path.join(settings.MEDIA_ROOT, 'hls', f'video_{video.id}', '720p', f"{stem}_720p.m3u8")
            hsl_test(out720,hls_dir_720)

            hls_dir_1080 = os.path.join(settings.MEDIA_ROOT, 'hls', f'video_{video.id}', '1080p', f"{stem}_1080p.m3u8")
            hsl_test(out1080,hls_dir_1080)

            rel480 = os.path.relpath(hls_dir_480, settings.MEDIA_ROOT)
            video.hls_480p.name = rel480

            rel720 = os.path.relpath(hls_dir_720, settings.MEDIA_ROOT)
            video.hls_720p.name = rel720

            rel1080 = os.path.relpath(hls_dir_1080, settings.MEDIA_ROOT)
            video.hls_1080p.name = rel1080

            video.save(update_fields=["hls_480p","hls_720p","hls_1080p"])



def delete_file(url):
    if url:
        if os.path.isfile(url.path):
            os.remove(url.path)


@receiver(post_delete, sender=Video)
def delete_video(sender, instance, **kwargs):
    delete_file(instance.thumbnail_url)
    delete_file(instance.video_file)
    hls_video_dir  = os.path.join(settings.MEDIA_ROOT, 'hls', f'video_{instance.id}')
    if os.path.isdir(hls_video_dir):
         shutil.rmtree(hls_video_dir)
