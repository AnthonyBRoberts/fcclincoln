from django.conf import settings
from django.core.files.storage import default_storage
from django.core.mail.message import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.http import HttpResponse
import time


class EMail(object):
    """
    A wrapper around Django's EmailMultiAlternatives
    that renders txt and html templates.
    Usage:
    >>> email = Email(to='oz@example.com', subject='A great non-spammy email!')
    >>> ctx = {'username': 'Oz Katz'}
    >>> email.text('templates/email.txt', ctx)
    >>> email.html('templates/email.html', ctx)  #Optional
    >>> email.add_attachment(attachment) #Optional
    >>> email.send()
    """
    def __init__(self, subject, to):
        self.subject = subject
        self.to = to
        self.bcc = None
        self._html = None
        self._text = None
        self._attachment = None

    def _render(self, template, context):
        return render_to_string(template, context)

    def html(self, template, context):
        self._html = self._render(template, context)

    def text(self, template, context):
        self._text = self._render(template, context)

    def add_attachment(self, attachment):
        self._attachment = default_storage.open(attachment.name, 'r')
        
    def send(self, from_addr=None, fail_silently=False):
        if isinstance(self.to, basestring):
            self.to = [self.to]
        if not from_addr:
            from_addr = getattr(settings, 'DEFAULT_FROM_EMAIL')
        msg = EmailMultiAlternatives(
            self.subject,
            self._text,
            from_addr,
            to=self.to,
            bcc=self.bcc,
        )
        if self._html:
            msg.attach_alternative(self._html, 'text/html')
        if self._attachment:
            msg.attach(self._attachment.name, self._attachment.read())
        msg.send()


def log_email(email, date_string):
    
    with open('static/email_logs/temp.txt', 'w') as tempFile:
        tempFile.write(email + "\n")
    f = open('static/email_logs/temp.txt', 'r')
    temp = f.read()
    f.close()
    with open('static/email_logs/sent_emails-' + date_string + '.txt', 'r') as f2:
        temp2 = f2.read()
    with open('static/email_logs/sent_emails-' + date_string + '.txt', 'w') as logFile:
        logFile.write(temp2 + temp)
