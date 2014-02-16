import datetime
import phonenumbers
from django import forms
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from localflavor.us.models import USStateField
from localflavor.us.us_states import STATE_CHOICES
from django.dispatch import receiver
from django.utils import timezone
from registration.signals import user_activated, user_registered
from notifications import notify
from account.tasks import new_client_alert

USER_TYPES = (
    ('Editor', 'Editor'),
    ('Reporter', 'Reporter'),
    ('Client', 'Client'),
    ('InactiveClient', 'InactiveClient'),
    ('InactiveReporter', 'InactiveReporter'),
)

PUB_TYPES = (
    ('Newspaper', 'Newspaper'),
    ('Radio', 'Radio'),
    ('Television', 'Television'),
    ('Online', 'Online'),
    ('Other', 'Other'),
)


class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True)
    user_type = models.CharField(max_length=25, choices=USER_TYPES, default='Client')
    can_publish = models.BooleanField(default=False)
    byline = models.CharField(max_length=75, blank=True, null=True)
    bio = models.CharField(max_length=2000, blank=True, null=True)
    """ Client Profile Fields """
    about = models.TextField(blank=True, null=True, verbose_name="Special Topics")
    address = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = USStateField(default="NE")
    zipcode = models.CharField(max_length=5, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    pub_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Publication Name")
    pub_type = models.CharField(max_length=10, choices=PUB_TYPES, blank=True, null=True)
    pub_area = models.CharField(max_length=100, blank=True, null=True, verbose_name="Circulation Area")
    twitter = models.CharField(max_length=150, blank=True, null=True)
    facebook = models.CharField(max_length=150, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)


    def get_absolute_url(self):
        return 'profiles_profile_detail', (), {'username': self.user.username}
    
    def formatted_phone(self, country=None):
        try:
            fphone = phonenumbers.parse(self.phone, 'US')
            if fphone is not None:
                return phonenumbers.format_number(fphone, phonenumbers.PhoneNumberFormat.NATIONAL)
        except:
            fphone = self.phone
            return fphone
        
    def __unicode__(self):
        return self.user.get_full_name()
    
    def save(self, *args, **kwargs):
        try:
            existing = UserProfile.objects.get(user=self.user)
            self.id = existing.id  # force update instead of insert
        except UserProfile.DoesNotExist:
            pass 
        models.Model.save(self, *args, **kwargs) 
    
    get_absolute_url = models.permalink(get_absolute_url)


@receiver(post_save, sender=User)
def create_profile(sender, **kwargs):
    user = kwargs['instance']
    if kwargs['created']:
        up = UserProfile(user=user)
        up.save()  


@receiver(user_activated)
def alert_editor_of_newclient(sender, user, request, **kwargs):
    subject = 'New Client Signup'
    client_email = user.email
    recipients = []
    for profile in UserProfile.objects.filter(user_type = 'Editor'):
        recipients.append(profile.user.email)
    new_client_alert.delay(settings.DEFAULT_FROM_EMAIL, recipients, subject, client_email)

@receiver(user_registered)
def user_registered_handler(sender, user, request, **kwargs):
    user.first_name = request.POST.get('first_name')
    user.last_name = request.POST.get('last_name')
    profile = user.get_profile()
    profile.about = request.POST.get('about')
    profile.address = request.POST.get('address')
    profile.city = request.POST.get('city')
    profile.state = request.POST.get('state')
    profile.zipcode = request.POST.get('zipcode')
    profile.phone = request.POST.get('phone')
    profile.pub_name = request.POST.get('pub_name')
    profile.pub_type = request.POST.get('pub_type')
    profile.pub_area = request.POST.get('pub_area')
    profile.twitter = request.POST.get('twitter')
    profile.facebook = request.POST.get('facebook')
    profile.website = request.POST.get('website')
    user.save()
    profile.save()

