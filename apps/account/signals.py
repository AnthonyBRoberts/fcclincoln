from django.dispatch import Signal
from registration.signals import user_activated
from django.conf import settings
from django.dispatch import receiver
from account.tasks import new_client_alert
from account.models import UserProfile
from django.contrib.auth.models import User


@receiver(user_activated, sender=User)
def alert_editor_of_newclient(sender, instance, created, **kwargs):
    user = kwargs['instance']
    subject = 'New Client Signup'
    client_email = user.user.email
    recipients = []
    for profile in UserProfile.objects.filter(user_type = 'Editor'):
        recipients.append(profile.user.email)
    new_client_alert.delay(settings.DEFAULT_FROM_EMAIL, recipients, subject, client_email)