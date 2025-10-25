import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

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
    from auth_app.api import signals 
    dummy = DummyQueue(execute_now=True)
    monkeypatch.setattr(signals.django_rq, "get_queue", lambda *a, **k: dummy)
    return dummy