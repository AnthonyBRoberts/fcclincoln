from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms import *
from django.forms import ModelForm
from django.contrib.admin import ModelAdmin
from suit_redactor.widgets import RedactorWidget
from django.db.models import *
from models import Article
from apps.account.models import UserProfile
from tinymce.widgets import TinyMCE
from taggit.models import Tag, TaggedItem


class ArticleAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ArticleAdminForm, self).__init__(*args, **kwargs)
        self.fields['author'].queryset = User.objects.filter(Q(userprofile__user_type = 'Reporter') | Q(userprofile__user_type = 'Editor'))
    class Meta:
        widgets = {
            'email_text': RedactorWidget(editor_options={'lang': 'en'}),
            'text': RedactorWidget(editor_options={'lang': 'en'}),
        }
        model = Article

    
class ArticleAdmin(ModelAdmin):
    form = ArticleAdminForm
    list_display = ('title', 'is_published', 'docfile')
    list_filter = ['author', 'is_published', ]
    search_fields = ['title', 'author',]
    date_hierarchy = 'publish_date'
    fieldsets = [
        (None, {'classes': ['edit'], 
            'fields': (('title', 'slug'), ('author', 'byline'),
                       ('publish_date', 'is_published', 'send_now'),
                       'docfile', 'tags', 'text', 'email_text'),
            }),
    ]


admin.site.register(Article, ArticleAdmin)



