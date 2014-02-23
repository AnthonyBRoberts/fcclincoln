from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView, ListView
from django.conf import settings
from django.contrib import admin
from registration.views import register
from registration_email.forms import EmailRegistrationForm
import notifications
from account.forms import *
from account.models import UserProfile
from story.models import Article
from story.views import *
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', FrontpageView.as_view()),
    url(r'^history/$', HistoryView.as_view()),
    url(r'^calendar/$', CalendarView.as_view()),
    url(r'^news/$', CalendarView.as_view()),
    url(r'^visitors/$', VisitorsView.as_view()),
    url(r'^ministries/$', MinistriesView.as_view()),
    url(r'^contact/$', ContactView.as_view()),
    url(r'^music/$', ContactView.as_view()),
    url(r'^worship/$', NewsView.as_view()),
    url(r'^sermons/$', NewsView.as_view()),
    url(r'^weddings/$', NewsView.as_view()),
    url(r'^church_life/$', NewsView.as_view()),
    url(r'^outreach/$', NewsView.as_view()),
    url(r'^ministry/children/$', NewsView.as_view()),
    url(r'^ministry/youth/$', NewsView.as_view()),
    url(r'^ministry/adults/$', NewsView.as_view()),
    url(r'^accounts/register/$',
        register,
        {'backend': 'registration.backends.default.DefaultBackend',
        'template_name': 'registration/registration_form.html',
        'form_class': ClientSignupForm,
        'success_url': getattr(
            settings, 'REGISTRATION_EMAIL_REGISTER_SUCCESS_URL', None),
        },
        name='registration_register', 
    ),
    url(r'^accounts/', include('registration_email.backends.default.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^reset/', include('password_reset.urls')),
    url(r'^admin/django-ses/', include('django_ses.urls')),
    url(r'^reporting/', include('django_ses.urls')),
    url(r'^story/', include('apps.story.urls')),
    url(r'^reporters/', 'account.views.reporter_index',
        name='profiles_reporter_list'),
    url(r'^editors/', 'account.views.editor_index',
        name='profiles_editor_list'),
    url(r'^profiles/', include('apps.account.urls')),
    ('^inbox/notifications/', include(notifications.urls)),
)

if getattr(settings,"DEBUG"):
    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )
