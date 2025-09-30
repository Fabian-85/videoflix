from django.core.mail import send_mail
from django.dispatch import receiver    
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
import django_rq


User = get_user_model()

def send_avtivation_mail():
    pass


@receiver(post_save, sender=User)
def registration_post_save(sender, instance, created, **kwargs):
    if created:
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(send_mail,"Test","Test Mail","fabian.maier2002@gmail.com", [instance.email],fail_silently=False)



 