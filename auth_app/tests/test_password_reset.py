import pytest
from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator


@pytest.mark.django_db
def test_password_reset_request(api_client, active_user,rq_queue):
    url = reverse("password_reset")
    resp = api_client.post(url, {"email": active_user.email}, format="json")
    assert resp.status_code == 200
    assert len(rq_queue.jobs) == 1
    fn, args, kwargs = rq_queue.jobs[0]
    assert fn.__name__ == "send_reset_password_mail"
    assert len(mail.outbox) == 1
    msg = mail.outbox[0]
    assert msg.subject == "Reset your Videoflix account"
    

@pytest.mark.django_db
def test_password_reset_request_with_unregistered_email(api_client,rq_queue):
    url = reverse("password_reset")
    resp = api_client.post(url, {"email": "unregister_user@mail.com"}, format="json")
    assert resp.status_code == 200
    assert len(rq_queue.jobs) == 0


@pytest.mark.django_db
def test_password_reset_confirm_success(api_client, active_user):
    uidb64 = urlsafe_base64_encode(force_bytes(active_user.pk))
    token = default_token_generator.make_token(active_user)
    url = reverse("password_confirm", kwargs={"uidb64": uidb64, "token": token})
    payload = {"new_password": "new_secret_password_123", "confirm_password": "new_secret_password_123"}
    resp = api_client.post(url, payload, format="json")
    active_user.refresh_from_db()
    assert resp.status_code == 200
    assert active_user.check_password("new_secret_password_123") is True


@pytest.mark.django_db
def test_password_reset_confirm_invalid_token(api_client, active_user):
    uidb64 = urlsafe_base64_encode(force_bytes(active_user.pk))
    url = reverse("password_confirm", kwargs={"uidb64": uidb64, "token": "wrong_token"})
    payload = {"new_password": "new_secret_password_123", "confirm_password": "new_secret_password_123"}
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == 200


@pytest.mark.django_db
def test_password_reset_confirm_invalid_user_and_valid_token_from_a_other_user(api_client, active_user):
    token = default_token_generator.make_token(active_user)
    url = reverse("password_confirm", kwargs={"uidb64": "invalid_uidb64", "token": token})
    payload = {"new_password": "new_secret_password_123", "confirm_password": "new_secret_password_123"}
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == 200
