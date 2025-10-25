import pytest
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
def test_logout_blacklists_and_deletes_cookies(api_client, active_user):
    refresh = RefreshToken.for_user(active_user)
    access = refresh.access_token
    api_client.cookies["refresh_token"] = str(refresh)
    api_client.cookies["access_token"] = str(access)
    url = reverse("logout")
    resp = api_client.post(url)
    assert resp.status_code == 200
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies
    assert resp.cookies["access_token"]["max-age"] == 0
    assert resp.cookies["refresh_token"]["max-age"] == 0

@pytest.mark.django_db
def test_logout_missing_refresh_cookie(api_client, active_user):
    refresh = RefreshToken.for_user(active_user)
    access = refresh.access_token
    api_client.cookies["access_token"] = str(access)
    url = reverse("logout")
    resp = api_client.post(url)
    assert resp.status_code == 400


@pytest.mark.django_db
def test_logout_missing_access_cookie(api_client, active_user):
    refresh = RefreshToken.for_user(active_user)
    api_client.cookies["refresh_token"] = str(refresh)
    url = reverse("logout")
    resp = api_client.post(url)
    assert resp.status_code == 401