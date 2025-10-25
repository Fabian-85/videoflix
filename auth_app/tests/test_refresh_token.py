import pytest
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

@pytest.mark.django_db
def test_refresh_access_token(api_client, active_user):
    refresh = RefreshToken.for_user(active_user)
    api_client.cookies["refresh_token"] = refresh
    url = reverse("token_refresh")
    resp = api_client.post(url)
    assert resp.status_code == 200
    assert "access_token" in resp.cookies
    
@pytest.mark.django_db
def test_refresh_missing_cookie(api_client):
    url = reverse("token_refresh")
    resp = api_client.post(url,)
    assert resp.status_code == 400
    assert "access_token" not in resp.cookies
    assert "refresh_token" not in resp.cookies

 