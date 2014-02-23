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
        queryset = UserProfile.objects.filter(user_type="Reporter")
        context['reporter_list'] = queryset
        return context

class HistoryView(DetailView):
    template_name="about.html"
    def get_object(self):
        return get_object_or_404(Article, slug="history")
    def get_context_data(self, **kwargs):
        context = super(HistoryView, self).get_context_data(**kwargs)
        context['slug'] = "history"
        return context

class CalendarView(DetailView):
    template_name="calendar.html"
    def get_object(self):
        return get_object_or_404(Article, slug="calendar")
    def get_context_data(self, **kwargs):
        context = super(CalendarView, self).get_context_data(**kwargs)
        context['slug'] = "calendar"
        return context

class VisitorsView(DetailView):
    template_name="about.html"
    def get_object(self):
        return get_object_or_404(Article, slug="visitors")
    def get_context_data(self, **kwargs):
        context = super(VisitorsView, self).get_context_data(**kwargs)
        context['slug'] = "visitors"
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
    template_name="about.html"
    def get_object(self):
        return get_object_or_404(Article, slug="contact")
    def get_context_data(self, **kwargs):
        context = super(ContactView, self).get_context_data(**kwargs)
        context['slug'] = "contact"
        return context

class NewsView(DetailView):
    template_name="about.html"
    def get_object(self):
        return get_object_or_404(Article, slug="news")
    def get_context_data(self, **kwargs):
        context = super(NewsView, self).get_context_data(**kwargs)
        context['slug'] = "news"
        return context

@login_required 
def inprogress_index(request):
    """
    Stories in progress view, a list of all stories in progress
    """
    inprogress_list = Article.objects.filter(is_published=False).order_by('-publish_date')
    paginator = Paginator(inprogress_list, 10)
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
    paginator = Paginator(story_list, 10)
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
        if request.user.get_profile().user_type == 'Reporter':
            form = Article_RForm(request.POST, request.FILES or None)
            form.author = request.user
            form.publish_date = datetime.datetime.now()
        elif request.user.get_profile().user_type == 'Editor':
            form = Article_EForm(request.POST, request.FILES or None)
        else:
            form = Article_RForm(request.POST, request.FILES or None)
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
            if request.user.get_profile().user_type == 'Editor':
                if article.is_published and article.send_now:
                    subject = article.title
                    byline = article.byline
                    email_text = article.email_text
                    story_text = article.text 
                    bc_only = form.cleaned_data['broadcast_only']
                    add_email_only = form.cleaned_data['add_recipients_only']
                    add_email_list = form.cleaned_data['add_recipients']
                    recipients = []
                    date_string = time.strftime("%Y-%m-%d-%H-%M")
                    if add_email_only:
                        for r in add_email_list:
                            recipients.append(r)
                    else: 
                        for profile in UserProfile.objects.filter(user_type = 'Editor'):
                            recipients.append(profile.user.email)
                        for profile in UserProfile.objects.filter(user_type = 'Reporter'):        
                            recipients.append(profile.user.email)
                        if bc_only:
                            for profile in UserProfile.objects.filter(Q(user_type = 'Client') & (Q(pub_type = 'Radio') | Q(pub_type = 'Television'))):
                                recipients.append(profile.user.email)
                        else:
                            for profile in UserProfile.objects.filter(user_type = 'Client'):        
                                recipients.append(profile.user.email)
                        if add_email_list:
                            for r in add_email_list:
                                recipients.append(r)
                    if article.docfile is not None:
                        attachment = article.docfile
                        create_email_batch.delay(date_string, request.user.email, recipients, subject,
                                                        byline, email_text, story_text, attachment)
                    else:
                        create_email_batch.delay(date_string, request.user.email, recipients, subject,
                                                        byline, email_text, story_text)
                    msg = "Article published successfully"
                    messages.success(request, msg, fail_silently=True)
            elif request.user.get_profile().user_type == 'Reporter':
                ready_for_editor = form.cleaned_data['ready_for_editor']
                if ready_for_editor:
                    subject = article.title + ' is ready for an editor'
                    byline = request.user.get_profile().byline
                    story_text = article.text 
                    alert_editor.delay(request.user.email, subject, byline, story_text)
                    msg = "Editor has been notified."
                    messages.success(request, msg, fail_silently=True)
            return redirect(article)
    else:
        if request.user.get_profile().user_type == 'Reporter':
            form = Article_RForm(initial={'byline': request.user.get_profile().byline})
        elif request.user.get_profile().user_type == 'Editor':
            form = Article_EForm(initial={'byline': request.user.get_profile().byline,
                         'email_text': '<p>Editors/News Directors:</p><p></p><p>Thank you,</p><p>Nebraska News Service</p>'})
            form.fields['author'].queryset = UserProfile.objects.filter(Q(user_type = 'Reporter') | Q(user_type = 'Editor'))
        else:
            form = Article_RForm(initial={'byline': request.user.get_profile().byline})
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
        if request.user.get_profile().user_type == 'Reporter':
            form = Article_RForm(request.POST, request.FILES, instance=article)
            form.publish_date = datetime.datetime.now()
        elif request.user.get_profile().user_type == 'Editor':
            form = Article_EForm(request.POST, request.FILES, instance=article)
        else:
            form = Article_RForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            cleaned_text = replace_all(article.text)
            article.text = cleaned_text
            article = form.save()
            msg = "Article updated successfully"
            messages.success(request, msg, fail_silently=True)
            if request.user.get_profile().user_type == 'Editor':
                if article.is_published and article.send_now:
                    subject = article.title
                    byline = article.byline
                    email_text = article.email_text
                    story_text = article.text
                    bc_only = form.cleaned_data['broadcast_only']
                    add_email_only = form.cleaned_data['add_recipients_only']
                    add_email_list = form.cleaned_data['add_recipients']
                    recipients = []
                    date_string = time.strftime("%Y-%m-%d-%H-%M")
                    if add_email_only:
                        for r in add_email_list:
                            recipients.append(r)
                    else: 
                        for profile in UserProfile.objects.filter(user_type = 'Editor'):
                            recipients.append(profile.user.email)
                        for profile in UserProfile.objects.filter(user_type = 'Reporter'):        
                            recipients.append(profile.user.email)
                        if bc_only:
                            for profile in UserProfile.objects.filter(Q(user_type = 'Client') & (Q(pub_type = 'Radio') | Q(pub_type = 'Television'))):
                                recipients.append(profile.user.email)
                        else:
                            for profile in UserProfile.objects.filter(user_type = 'Client'):        
                                recipients.append(profile.user.email)
                        if add_email_list:
                            for r in add_email_list:
                                recipients.append(r)
                    if article.docfile is not None:
                        attachment = article.docfile
                        create_email_batch.delay(date_string, request.user.email, recipients, subject,
                                                        byline, email_text, story_text, attachment)
                    else:
                        create_email_batch.delay(date_string, request.user.email, recipients, subject,
                                                        byline, email_text, story_text)
                    msg = "Article published successfully"
                    messages.success(request, msg, fail_silently=True)
            elif request.user.get_profile().user_type == 'Reporter':
                ready_for_editor = form.cleaned_data['ready_for_editor']
                if ready_for_editor:
                    subject = article.title + ' is ready for an editor'
                    byline = request.user.get_profile().byline
                    story_text = article.text 
                    alert_editor.delay(request.user.email, subject, byline, story_text)
                    msg = "Editor has been notified."
                    messages.success(request, msg, fail_silently=True)
            return redirect(article)
    else:
        if request.user.get_profile().user_type == 'Reporter':
            form = Article_RForm(instance=article, initial={'byline': article.author.get_profile().byline})
        elif request.user.get_profile().user_type == 'Editor':
            if article.email_text:
                form = Article_EForm(instance=article, initial={'email_text': article.email_text})
                form.fields['author'].queryset = UserProfile.objects.filter(Q(user_type = 'Reporter') | Q(user_type = 'Editor'))
            else:
                form = Article_EForm(instance=article,
                    initial={'byline': article.author.get_profile().byline,
                             'email_text': '<p>Editors/News Directors:</p><p></p><p>Thank you,</p><p>Nebraska News Service</p>'})
                form.fields['author'].queryset = UserProfile.objects.filter(Q(user_type = 'Reporter') | Q(user_type = 'Editor'))
        else:
            form = Article_RForm(instance=article, initial={'byline': article.author.get_profile().byline})
    return render_to_response('story/article_form.html', 
                              { 
                                  'form': form,
                                  'article': article,
                              },
                              context_instance=RequestContext(request))