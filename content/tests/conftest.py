import pytest
from pathlib import Path
from django.core.files import File
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from content.models import Video


@pytest.fixture(autouse=True)
def media_root_tmp(tmp_path, settings):
    settings.MEDIA_ROOT = str(tmp_path / "media")
    (tmp_path / "media").mkdir(parents=True, exist_ok=True)
    return tmp_path

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def UserModel():
    return get_user_model()

@pytest.fixture
def active_user(UserModel, django_db_blocker):
    with django_db_blocker.unblock():
        user = UserModel.objects.create_user(
            username="active_user@example.com",
            email="active@example.com",
            password="secretpassword123",
            is_active=True,
        )
        return user
    
@pytest.fixture
def inactive_user(UserModel, django_db_blocker):
    with django_db_blocker.unblock():
        user = UserModel.objects.create_user(
            username="inactive@example.com",
            email="inactive@example.com",
            password="secretpassword123",
            is_active=False,
        )
        return user
    
@pytest.fixture(autouse=True)
def email_locmem_backend(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "no-reply@test.local"
    settings.FRONTEND_URL = "https://frontend.test"
    return settings


class DummyQueue:
    def __init__(self, execute_now: bool = False):
        self.execute_now = execute_now
        self.jobs = [] 

    def enqueue(self, fn, *args, **kwargs):
        self.jobs.append((fn, args, kwargs))
        if self.execute_now:
            fn(*args, **kwargs)

@pytest.fixture
def rq_queue(monkeypatch):
    from content.api import signals 
    dummy = DummyQueue(execute_now=True)
    monkeypatch.setattr(signals.django_rq, "get_queue", lambda *a, **k: dummy)
    return dummy

@pytest.fixture
def create_test_videos(rq_queue, django_db_blocker):
    with django_db_blocker.unblock():   
     assets = Path(__file__).resolve().parent / "test_files"
     video_src = assets / "videos" / "video_1.mp4"
     thumb_src = assets / "thumbnails" / "thumbnail_1.png"
     
     
     with open(video_src, "rb") as vf, open(thumb_src, "rb") as tf:
        v1 = Video.objects.create(
            title="First Video",
            description="description",
            video_file=File(vf, name="video1.mp4"),
            thumbnail_url=File(tf, name="thumbnail1.jpg"),
        )
        v2 = Video.objects.create(
            title="Second Video",
            description="description",
            video_file=File(vf, name="video1.mp4"),
            thumbnail_url=File(tf, name="thumbnail2.jpg"),
        )
        v1.refresh_from_db()
        v2.refresh_from_db()
        return v1, v2