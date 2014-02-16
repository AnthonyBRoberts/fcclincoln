from django import forms
from django.core.validators import validate_email
from models import Article
from django.contrib.admin import widgets
from datetimewidget.widgets import DateTimeWidget
from suit_redactor.widgets import RedactorWidget

class MultiEmailField(forms.Field):
    def to_python(self, value):
        "Normalize data to a list of strings."

        # Return an empty list if no input was given.
        if not value:
            return []
        return value.split(',')

    def validate(self, value):
        "Check if value consists only of valid emails."

        # Use the parent's handling of required fields, etc.
        super(MultiEmailField, self).validate(value)

        for email in value:
            validate_email(email.strip(' '))

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['author', 'slug']
        dateTimeOptions = {
            'format': 'mm/dd/yyyy HH:ii P',
            'autoclose': 'true',
            'showMeridian': 'false',
        }
        widgets = {
            'email_text': RedactorWidget(editor_options={'lang': 'en'}),
            'text': RedactorWidget(editor_options={'lang': 'en'}),
        }


class Article_EForm(forms.ModelForm):

    broadcast_only = forms.BooleanField(label='Send to Broadcast Only', required=False)
    add_recipients_only = forms.BooleanField(label='Send to Additional Recipients Only', required=False)
    add_recipients = MultiEmailField(label='Additional Recipients, multiple emails must be separated by a comma.', required=False)

    def clean(self):
        cleaned_data = super(Article_EForm, self).clean()
        add_recipients = cleaned_data.get("add_recipients")
        add_recipients_only = cleaned_data.get("add_recipients_only")

        if add_recipients_only:
            if add_recipients == []:
                raise forms.ValidationError("You selected Send to Additional Recipients Only, but didn't include any additional recipients")
        return cleaned_data

    class Meta:
        model = Article
        fields = ('title', 'text', 'email_text', 'author', 'byline',
                    'tags', 'docfile', 'publish_date', 'is_published', 
                    'send_now', 'broadcast_only', 'add_recipients_only', 'add_recipients'
                    )
        exclude = ['slug']
        dateTimeOptions = {
            'format': 'mm/dd/yyyy HH:ii P',
            'autoclose': 'true',
            'showMeridian': 'false',
        }
        widgets = {
            'publish_date': DateTimeWidget(options = dateTimeOptions),
            'email_text': RedactorWidget(editor_options={'lang': 'en'}),
            'text': RedactorWidget(editor_options={'lang': 'en'}),
        }


class Article_RForm(forms.ModelForm):

    ready_for_editor = forms.BooleanField(label='Ready for editor', required=False)

    class Meta:
        model = Article
        fields = ('title', 'text', 'tags', 'docfile', 'ready_for_editor')
        exclude = ['author', 'byline', 'slug', 'publish_date', 'email_text', 'is_published', 'send_now']
        dateTimeOptions = {
            'format': 'mm/dd/yyyy HH:ii P',
            'autoclose': 'true',
            'showMeridian': 'false',
        }
        widgets = {
            'text': RedactorWidget(editor_options={'lang': 'en'})
        }