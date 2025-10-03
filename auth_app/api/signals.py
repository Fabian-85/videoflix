from django.core.mail import send_mail
from django.dispatch import receiver    
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
import django_rq
from django.conf import settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

def send_avtivation_mail():
    pass


@receiver(post_save, sender=User)
def registration_post_save(sender, instance, created, **kwargs):
    if created:
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(send_mail,"Videoflix Konto Aktivierung","", getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"), [instance.email],fail_silently=False)





 
 
 
 
 




from .signals_def import password_reset_requested

@receiver(password_reset_requested)
def handle_password_reset_requested(sender, request, user,**kwargs):
     print(1)
     uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
     token = default_token_generator.make_token(user)
     print(1)
     activate_path = reverse("password_confirm", kwargs={"uidb64": uidb64, "token": token})
     activate_url = request.build_absolute_uri(activate_path)
     print(1)
     queue = django_rq.get_queue("default", autocommit=True)
     queue.enqueue(send_mail,'password rest',activate_url,getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),[user.email],fail_silently=False)


 