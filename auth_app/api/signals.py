from .signals_def import password_reset_requested, email_verification_requested
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.dispatch import receiver
from django.conf import settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
import django_rq

User = get_user_model()


@receiver(email_verification_requested)
def handle_email_verification_requested(sender, user, email, token, request, **kwargs):
     uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
     activate_path = reverse("activate_account", kwargs={"uidb64": uidb64, "token": token})
     activate_url = request.build_absolute_uri(activate_path)
     queue = django_rq.get_queue('default', autocommit=True)
     confirmation_url = f"{settings.FRONTEND_URL}/pages/auth/activate.html?uid={uidb64}&token={token}"
     queue.enqueue(send_mail, "Videoflix Konto Aktivierung", confirmation_url, getattr(
            settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"), [email], fail_silently=False)


@receiver(password_reset_requested)
def handle_password_reset_requested(sender, request, user, **kwargs):
    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    activate_path = reverse("password_confirm", kwargs={"uidb64": uidb64, "token": token})
    activate_url = request.build_absolute_uri(activate_path)
    confirmation_url = f"{settings.FRONTEND_URL}/pages/auth/confirm_password.html?uid={uidb64}&token={token}"
    queue = django_rq.get_queue("default", autocommit=True)
    queue.enqueue(send_mail, 'password rest', confirmation_url, getattr(
        settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"), [user.email], fail_silently=False)
