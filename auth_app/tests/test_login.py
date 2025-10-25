import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login_success(api_client, active_user):
    url = reverse("login")
    payload = {
        "email": active_user.email,
        "password": "secretpassword123"
    }
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == 200
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies


@pytest.mark.django_db
def test_login_with_wrong_password(api_client,active_user):
    url = reverse("registration")
    payload = {
        "email": active_user.email,
        "password": "wrong_password",
    }
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_login_with_wrong_email(api_client,active_user):
    url = reverse("registration")
    payload = {
        "email": "user@mail.com",
        "password": "secretpassword123",
    }
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_login_with_inactive_account(api_client,inactive_user):
    url = reverse("registration")
    payload = {
        "email": inactive_user.email,
        "password": "secretpassword123",
    }
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == 400