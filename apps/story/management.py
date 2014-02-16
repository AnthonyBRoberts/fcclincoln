from django.conf import settings
from django.db.models import signals
from django.utils.translation import ugettext_noop as _

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("reporter_story_update", _("Reporter Story Update"), _("A reporter has updated a story"))
        notification.create_notice_type("editor_story_update", _("Editor Story Update"), _("An editor has updated your story"))

    signals.post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"