import os
import redis
import time
import datetime
from tools.killgremlins import killgremlins, replace_all
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.encoding import smart_str, smart_unicode, force_unicode
from django.views.generic import DetailView, ListView
from django.views.generic.detail import SingleObjectMixin
from notification import models as notification
from story.models import Article
from story.forms import *
from story.tasks import create_email_batch, alert_editor
from apps.account.models import UserProfile


class FrontpageView(DetailView):
    template_name = "welcome_content.html"
    def get_object(self):
        return get_object_or_404(Article, slug="front-page")
    def get_context_data(self, **kwargs):
        context = super(FrontpageView, self).get_context_data(**kwargs)
        context['slug'] = "front-page"
        events = Article.objects.filter(slug="events")
        context['events'] = events
        return context

class HistoryView(DetailView):
    template_name="about.html"
    def get_object(self):
        return get_object_or_404(Article, slug="history")
    def get_context_data(self, **kwargs):
        context = super(HistoryView, self).get_context_data(**kwargs)
        context['slug'] = "history"
        events = Article.objects.filter(slug="events")
        context['events'] = events
        return context

class CalendarView(DetailView):
    template_name="calendar.html"
    def get_object(self):
        return get_object_or_404(Article, slug="calendar")
    def get_context_data(self, **kwargs):
        context = super(CalendarView, self).get_context_data(**kwargs)
        context['slug'] = "calendar"
        events = Article.objects.filter(slug="events")
        context['events'] = events
        return context

class VisitorsView(DetailView):
    template_name="welcomev.html"
    def get_object(self):
        return get_object_or_404(Article, slug="visitors")
    def get_context_data(self, **kwargs):
        context = super(VisitorsView, self).get_context_data(**kwargs)
        context['slug'] = "visitors"
        events = Article.objects.filter(slug="events")
        context['events'] = events
        return context

class MinistriesView(DetailView):
    template_name="about.html"
    def get_object(self):
        return get_object_or_404(Article, slug="ministries")
    def get_context_data(self, **kwargs):
        context = super(MinistriesView, self).get_context_data(**kwargs)
        context['slug'] = "ministries"
        return context

class ContactView(DetailView):
    template_name="no_image.html"
    def get_object(self):
        return get_object_or_404(Article, slug="contact")
    def get_context_data(self, **kwargs):
        context = super(ContactView, self).get_context_data(**kwargs)
        context['slug'] = "contact"
        return context

class StaffView(DetailView):
    template_name="no_image.html"
    def get_object(self):
        return get_object_or_404(Article, slug="staff")
    def get_context_data(self, **kwargs):
        context = super(StaffView, self).get_context_data(**kwargs)
        context['slug'] = "staff"
        events = Article.objects.filter(slug="events")
        context['events'] = events
        return context

class NewsView(DetailView):
    template_name="about.html"
    def get_object(self):
        return get_object_or_404(Article, slug="news")
    def get_context_data(self, **kwargs):
        context = super(NewsView, self).get_context_data(**kwargs)
        context['slug'] = "news"
        return context

class MusicView(DetailView):
    template_name="music.html"
    def get_object(self):
        return get_object_or_404(Article, slug="music")
    def get_context_data(self, **kwargs):
        context = super(MusicView, self).get_context_data(**kwargs)
        context['slug'] = "music"
        events = Article.objects.filter(slug="events")
        context['events'] = events
        return context

class WorshipView(DetailView):
    template_name="worship.html"
    def get_object(self):
        return get_object_or_404(Article, slug="worship")
    def get_context_data(self, **kwargs):
        context = super(WorshipView, self).get_context_data(**kwargs)
        context['slug'] = "worship"
        events = Article.objects.filter(slug="events")
        context['events'] = events
        return context

class ChurchLifeView(DetailView):
    template_name="music.html"
    def get_object(self):
        return get_object_or_404(Article, slug="church-life")
    def get_context_data(self, **kwargs):
        context = super(ChurchLifeView, self).get_context_data(**kwargs)
        context['slug'] = "church-life"
        return context

class WeddingsView(DetailView):
    template_name="weddings.html"
    def get_object(self):
        return get_object_or_404(Article, slug="weddings")
    def get_context_data(self, **kwargs):
        context = super(WeddingsView, self).get_context_data(**kwargs)
        context['slug'] = "weddings"
        events = Article.objects.filter(slug="events")
        context['events'] = events
        return context

class OutreachView(DetailView):
    template_name="outreach.html"
    def get_object(self):
        return get_object_or_404(Article, slug="outreach")
    def get_context_data(self, **kwargs):
        context = super(OutreachView, self).get_context_data(**kwargs)
        context['slug'] = "outreach"
        return context

class ChildrenView(DetailView):
    template_name="music.html"
    def get_object(self):
        return get_object_or_404(Article, slug="children")
    def get_context_data(self, **kwargs):
        context = super(ChildrenView, self).get_context_data(**kwargs)
        context['slug'] = "children"
        return context

class YouthView(DetailView):
    template_name="music.html"
    def get_object(self):
        return get_object_or_404(Article, slug="youth")
    def get_context_data(self, **kwargs):
        context = super(YouthView, self).get_context_data(**kwargs)
        context['slug'] = "youth"
        return context

class AdultsView(DetailView):
    template_name="music.html"
    def get_object(self):
        return get_object_or_404(Article, slug="adults")
    def get_context_data(self, **kwargs):
        context = super(AdultsView, self).get_context_data(**kwargs)
        context['slug'] = "adults"
        return context

class SermonsView(SingleObjectMixin, ListView):
    paginate_by = 2
    template_name="sermons.html"

    def get(self, request, *args, **kwargs):
        self.object = get_object_or_404(Article, slug="sermons")
        return super(SermonsView, self).get(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super(SermonsView, self).get_context_data(**kwargs)
        context['sermons_page'] = self.object
        queryset2 = Article.objects.filter(slug="events")
        context['events'] = queryset2
        return context
    def get_queryset(self):
        return Article.objects.filter(is_published=True).order_by('-publish_date')

def sermon_detail_view(request, slug):
    sermon = get_object_or_404(Article, slug=slug)
    events = Article.objects.filter(slug="events")
    return render_to_response('story/article_detail.html', 
                              {'events': events, 'sermon': sermon},
                              context_instance=RequestContext(request))

@login_required 
def inprogress_index(request):
    """
    Stories in progress view, a list of all stories in progress
    """
    inprogress_list = Article.objects.filter(is_published=False).order_by('-publish_date')
    paginator = Paginator(inprogress_list, 20)
    page = request.GET.get('page')
    try:
        show_lines = paginator.page(page)
    except PageNotAnInteger:
        show_lines = paginator.page(1)
    except EmptyPage:
        show_lines = paginator.page(paginator.num_pages)
    return render_to_response('story/article_inprogress_list.html', RequestContext(request, {
        'lines': show_lines, 'inprogress_list': inprogress_list,
    }))


@login_required 
def story_index(request):
    """
    Story index view, a list of all published stories
    """
    story_list = Article.objects.filter(is_published=True).order_by('-publish_date')
    paginator = Paginator(story_list, 20)
    page = request.GET.get('page')
    try:
        show_lines = paginator.page(page)
    except PageNotAnInteger:
        show_lines = paginator.page(1)
    except EmptyPage:
        show_lines = paginator.page(paginator.num_pages)
    return render_to_response('story/article_list.html', RequestContext(request, {
        'lines': show_lines, 
    }))


@login_required 
def add_article(request):
    """
    Create new article
    """
    if request.method == 'POST':
        form = Article_EForm(request.POST, request.FILES or None)
        form.author = request.user
        form.publish_date = datetime.datetime.now()
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            if article.is_published:
                article.publish_date = datetime.datetime.now()
            cleaned_text = replace_all(article.text)
            article.text = cleaned_text
            article.save()
            form.save_m2m()
            msg = "Article saved successfully"
            messages.success(request, msg, fail_silently=True)
            if article.is_published:
                msg = "Article published successfully"
                messages.success(request, msg, fail_silently=True)
            return redirect(article)
    else:
        form = Article_EForm(initial={'byline': request.user.get_profile().byline})
        form.fields['author'].queryset = UserProfile.objects.filter(Q(user_type = 'Reporter') | Q(user_type = 'Editor'))
    return render_to_response('story/article_form.html', 
                              { 'form': form },
                              context_instance=RequestContext(request))

@login_required 
def edit_article(request, slug):
    """
    Update existing article
    """
    article = get_object_or_404(Article, slug=slug)
    if request.method == 'POST':
        form = Article_EForm(request.POST, request.FILES, instance=article)
        form.publish_date = datetime.datetime.now()
        if form.is_valid():
            cleaned_text = replace_all(article.text)
            article.text = cleaned_text
            article = form.save()
            msg = "Article updated successfully"
            messages.success(request, msg, fail_silently=True)
            if article.is_published:
                msg = "Article published successfully"
                messages.success(request, msg, fail_silently=True)
            return redirect(article)
    else:
        form = Article_EForm(instance=article)
        form.fields['author'].queryset = UserProfile.objects.filter(Q(user_type = 'Reporter') | Q(user_type = 'Editor'))
    return render_to_response('story/article_form.html', 
                              { 
                                  'form': form,
                                  'article': article,
                              },
                              context_instance=RequestContext(request))