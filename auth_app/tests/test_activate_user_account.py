import pytest
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from auth_app.api.tokens import account_activation_token

@pytest.mark.django_db
def test_activate_account_success(api_client, inactive_user):
    uidb64 = urlsafe_base64_encode(force_bytes(inactive_user.pk))
    token = account_activation_token.make_token(inactive_user)
    url = reverse("activate_account", kwargs={"uidb64": uidb64, "token": token})
    resp = api_client.get(url)
    assert resp.status_code == 200
    inactive_user.refresh_from_db()
    assert inactive_user.is_active is True

@pytest.mark.django_db
def test_activate_account_invalid_token(api_client, inactive_user):
    uidb64 = urlsafe_base64_encode(force_bytes(inactive_user.pk))
    bad_token = "wrong_token"
    url = reverse("activate_account", kwargs={"uidb64": uidb64, "token": bad_token})

    resp = api_client.get(url)
    assert resp.status_code == 400
    inactive_user.refresh_from_db()
    assert inactive_user.is_active is False
