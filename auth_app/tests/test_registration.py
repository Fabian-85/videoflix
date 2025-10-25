import pytest
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_register_success(api_client, UserModel,rq_queue):
    url = reverse("registration")
    payload = {
        "email": "fabian.maier2002@gmail.com",
        "password": "secure_password",
        "confirmed_password": "secure_password",
    }
    resp = api_client.post(url, payload, format="json")
    data = resp.json()
    uid = data["user"]["user_id"]

    assert resp.status_code == 201
    user = UserModel.objects.get(pk=uid)
    assert user.is_active is False

    assert len(rq_queue.jobs) == 1
    fn, args, kwargs = rq_queue.jobs[0]
    assert fn.__name__ == "send_activation_email_task"
    assert len(mail.outbox) == 1
    msg = mail.outbox[0]
    assert msg.subject == "Activate your Videoflix account"
    assert payload["email"] in msg.to


@pytest.mark.django_db
def test_register_password_mismatch(api_client):
    url = reverse("registration")
    payload = {
        "email": "user@mail.com",
        "password": "secure_password",
        "confirmed_password": "wrong_password",
    }
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == 400
    assert "confirmed_password" in resp.json()


@pytest.mark.django_db
def test_register_duplicate_email_with_active_user(active_user, api_client):
    url = reverse("registration")
    payload = {
        "email": active_user.email,
        "password": "secure_password",
        "confirmed_password": "secure_password",
    }
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == 400
    assert "email" in resp.json()


@pytest.mark.django_db
def test_register_duplicate_email_with_inactive_user(inactive_user, api_client):
    url = reverse("registration")
    payload = {
        "email": inactive_user.email,
        "password": "secure_password",
        "confirmed_password": "secure_password",
    }
    api_client = APIClient()
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == 400
    assert "email" in resp.json()


