from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.conf import settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
import django_rq
from .signals_def import password_reset_requested, email_verification_requested
from .functions import send_activation_email_task, send_reset_password_mail


User = get_user_model()


@receiver(email_verification_requested)
def handle_email_verification_requested(sender, user, email, token, request, **kwargs):

    """
    On email verification signal, build uidb64, create a url for activate a user account
    and enqueue verification email task.
    """

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    activate_path = reverse("activate_account", kwargs={
                            "uidb64": uidb64, "token": token})
    activate_url = request.build_absolute_uri(activate_path)
    confirmation_url = f"{settings.FRONTEND_URL}/pages/auth/activate.html?uid={uidb64}&token={token}"
    queue = django_rq.get_queue('default', autocommit=True)
    queue.enqueue(send_activation_email_task, user.username, confirmation_url, email)


@receiver(password_reset_requested)
def handle_password_reset_requested(sender, request, user, **kwargs):

    """
    On password reset signal, build uidb64 + token, create a url for change the password
    and enqueue reset email task.
    """

    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    activate_path = reverse("password_confirm", kwargs={
                            "uidb64": uidb64, "token": token})
    activate_url = request.build_absolute_uri(activate_path)
    confirmation_url = f"{settings.FRONTEND_URL}/pages/auth/confirm_password.html?uid={uidb64}&token={token}"
    queue = django_rq.get_queue("default", autocommit=True)
    queue.enqueue(send_reset_password_mail, confirmation_url, user.email)
