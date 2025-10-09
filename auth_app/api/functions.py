from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings


def send_activation_email_task(username, confirmation_url, to_email):

    """
    Send activation email for activate a user account.

     Args:
        username: greeting name.
        confirmation_url: frontend link with uid+token to activate a user account.
        to_email: EN recipient.
    """

    subject = "Activate your Videoflix account"
    ctx = {"username": username, "activation_link": confirmation_url,
           "logo_url": getattr(settings, "EMAIL_LOGO_URL", None)}
    text_body = render_to_string("activation_account/activation_mail.txt", ctx)
    html_body = render_to_string("activation_account/activation_mail.html", ctx)
    send_mail(subject=subject, message=text_body, html_message=html_body,
              from_email=getattr(
                  settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
              recipient_list=[to_email], fail_silently=False)
    

def send_reset_password_mail(confirmation_url, to_email):

    """
    Send password reset email for change the password. 
   
    Args:
        confirmation_url: frontend link with uid+token to change the password.
        to_email: EN recipient.
    """
    subject="Reset your Videoflix account"
    ctx = { "reset_link": confirmation_url,
           "logo_url": getattr(settings, "EMAIL_LOGO_URL", None)}
    text_body = render_to_string("reset_password/reset_mail.txt", ctx)
    html_body = render_to_string("reset_password/reset_mail.html", ctx)
    send_mail(subject=subject, message=text_body, html_message=html_body,
              from_email=getattr(
                  settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
              recipient_list=[to_email], fail_silently=False)