from django.core.urlresolvers import reverse
import django.http
from django.conf.urls import patterns, url
from account.models import *
from account.forms import *


urlpatterns = patterns('',
    url(r'^(?P<username>\w+)/$',
        'profiles.views.profile_detail',
        name='profiles_profile_detail'),
    url('^client/create', 'account.views.create_profile',
        {
          'form_class': ClientForm,
          'success_url': 'profiles/client/edit/',
        },
        name='create_client_profile'),
    url('^client/edit', 'profiles.views.edit_profile',
        {
            'form_class': ClientForm,
        },
        name='edit_client_profile'),
    url('^unsubscribe', 'profiles.views.edit_profile',
        {
            'form_class': UnsubscribeForm,
            'success_url': '/profiles/client/edit/',
            'template_name': 'profiles/unsubscribe.html',
        },
        name='unsubscribe'),
    url('^reporter/edit', 'profiles.views.edit_profile',
        {
            'form_class': ReporterForm,
        },
        name='edit_reporter_profile'),                 
    url(r'^create/$',
       'profiles.views.create_profile',
       name='profiles_create_profile'),
    url(r'^edit/$',
       'profiles.views.edit_profile',
       name='profiles_edit_profile'),
    url(r'^$',
       'account.views.client_index',
       name='profiles_profile_list'),
    )