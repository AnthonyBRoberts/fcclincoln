from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save
from tinymce import models as tinymce_models
from taggit.managers import TaggableManager
from tools.killgremlins import killgremlins
from notifications import notify
import datetime



class PublishedArticlesManager(models.Manager):
    
    def get_query_set(self):
        return super(PublishedArticlesManager, self).get_query_set().filter(is_published=True)

class Article(models.Model):
    """Represents a story article"""
    
    title = models.CharField(max_length=255, verbose_name="Title")
    slug = models.SlugField(max_length=255, unique=True)
    text = models.CharField(max_length=40000, verbose_name="Message Text")
    email_text = models.CharField(max_length=10000, blank=True, null=True, verbose_name="Email Message Text")
    author = models.ForeignKey(User)
    byline = models.CharField(max_length=100, blank=True, null=True)
    is_published = models.BooleanField(default=False, verbose_name="Publish Story")
    send_now = models.BooleanField(default=False, verbose_name="Send Now?")
    created_on = models.DateTimeField(auto_now_add=True)
    publish_date = models.DateTimeField(default=datetime.datetime.now())
    objects = models.Manager()
    published = PublishedArticlesManager()
    docfile = models.FileField(upload_to='docs/%Y/%m/%d/', blank=True, null=True, verbose_name="Add Attachment")
    tags = TaggableManager(blank=True)

    def __unicode__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        #self.text = self.text.decode('cp1252')
        if not self.slug:
            y = self.publish_date.strftime("%Y")
            m = self.publish_date.strftime("%b").lower()
            d = self.publish_date.strftime("%d")
            self.slug = slugify(self.title) + "-" + d  + "-" + m  + "-" + y
        super(Article, self).save(*args, **kwargs)

    @models.permalink 
    def get_absolute_url(self):
        return ('story_article_detail', (), { 'slug': self.slug })
