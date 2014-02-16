import django
import django.contrib
from django import forms
import django.forms.fields
import django.forms.widgets
import django.db
from models import *
from suit_redactor.widgets import RedactorWidget
from localflavor.us.forms import USStateField, USStateSelect
from registration_email.forms import *
from bootstrap_toolkit.widgets import BootstrapTextInput

class ClientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        try:
            self.initial['email'] = self.instance.user.email
            self.initial['first_name'] = self.instance.user.first_name
            self.initial['last_name'] = self.instance.user.last_name
            self.initial['user_type'] = self.instance.user.get_profile().user_type
            self.initial['state'] = "NE"
        except User.DoesNotExist:
            pass
        
    email = forms.EmailField(label='Primary Email',
                             help_text='Where we will send new stories')
    first_name = forms.CharField(label='First name')
    last_name = forms.CharField(label='Last name')
    pub_name = forms.CharField(label='News organization name')
    pub_type = forms.ChoiceField(choices=PUB_TYPES, label='News media type')
    subscribe = forms.BooleanField(label='Subscribe to NNS Emails', required=False, initial=True)
    
    class Meta:
        model = UserProfile
        password = forms.CharField(label='Password', help_text='')
        about = forms.CharField(label='Special Topics',
                                help_text='Any special topics of interest to your audience?')
        
        fields = ['pub_name','pub_type','first_name','last_name','email',
                  'phone','address','city','state','zipcode','pub_area',
                  'about','twitter','facebook','website']
        exclude = ['user','user_type','can_publish','bio','byline',
                   'last_login','date_joined','is_staff','is_active',
                   'is_superuser','groups','user_permissions']
        
    def save(self, *args, **kwargs):
        """
        Update the primary email address, first & last name on the related User object as well.
        """
        u = self.instance.user
        p = self.instance.user.get_profile()
        u.email = self.cleaned_data['email']
        u.first_name = self.cleaned_data['first_name']
        u.last_name = self.cleaned_data['last_name']
        if self.cleaned_data['subscribe']:
            p.user_type = 'Client'
        u.save()
        p.save()
        

class ClientSignupForm(EmailRegistrationForm):        

    email = forms.EmailField(
        max_length=256,
        required=True,
        widget=forms.TextInput(attrs={'class':'email'}),
        label="Email"
        )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class':'password'}, render_value=False),
        label="Password"
        )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class':'password'}, render_value=False),
        label="Password (repeat)"
        )
    your_name = forms.CharField(required=False)
    pub_name = forms.CharField(label='News organization name', required=True)
    pub_type = forms.ChoiceField(
        choices=PUB_TYPES, 
        label='News media type', 
        required=True
        )
    first_name = forms.CharField(label='First name', required=True)
    last_name = forms.CharField(label='Last name', required=True)
    address = forms.CharField(max_length=100, required=True)
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(
        widget=USStateSelect(),
        initial="NE", 
        required=True
        )
    zipcode = forms.CharField(
        max_length=5, 
        required=True,
        widget=BootstrapTextInput(attrs={'class':'zipcode'})
        )
    phone = forms.CharField(max_length=15, required=True)
    pub_area = forms.CharField(
        max_length=100,
        required=True,
        label="Circulation or Broadcast Area",
        widget=BootstrapTextInput(attrs={'class':'circarea'})
        )
    about = forms.CharField(
        required=False, 
        label="Special Topics of interest to your audience. (optional)",
        widget=BootstrapTextInput(attrs={
            'class':'specialtopics',
            })
        )
    twitter = forms.CharField(
        max_length=150,
        required=False,
        label="Twitter (optional)",
        widget=BootstrapTextInput(attrs={'class':'website'})
        )
    facebook = forms.CharField(
        max_length=150,
        required=False,
        label="Facebook (optional)",
        widget=BootstrapTextInput(attrs={'class':'website'})
        )
    website = forms.URLField(
        max_length=200,
        required=False,
        label="Website (optional)",
        widget=BootstrapTextInput(attrs={'class':'website'})
        )


class ReporterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ReporterForm, self).__init__(*args, **kwargs)
        try:
            self.initial['email'] = self.instance.user.email
            self.initial['first_name'] = self.instance.user.first_name
            self.initial['last_name'] = self.instance.user.last_name
        except User.DoesNotExist:
            pass
    email = forms.EmailField(label='Primary email',
                             help_text='Your NNS Email Account')
    first_name = forms.CharField(label='First name')
    last_name = forms.CharField(label='Last name')
    class Meta:
        model = UserProfile
        password = forms.CharField(label='Password', help_text='')
        bio = forms.CharField(label='Reporter beats',
                                help_text='What will you focus on in your reporting?')
        widgets = {'bio': RedactorWidget(editor_options={'lang': 'en'})}
        fields = ['first_name','last_name','email','phone','bio','byline']
        exclude = ['pub_name','pub_type','user','user_type','can_publish','about',
                   'last_login','date_joined','is_staff','is_active',
                   'address','city','state','zipcode','pub_area','twitter','facebook','website',
                   'is_superuser','groups','user_permissions'] 
    def save(self, *args, **kwargs):
        """
        Update the primary email address, first & last name on the related User object as well.
        """
        u = self.instance.user
        u.email = self.cleaned_data['email']
        u.first_name = self.cleaned_data['first_name']
        u.last_name = self.cleaned_data['last_name']
        u.save()
        reporter = super(ReporterForm, self).save(*args,**kwargs)
        return reporter


class UnsubscribeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UnsubscribeForm, self).__init__(*args, **kwargs)
        try:
            self.initial['email'] = self.instance.user.email
            self.initial['first_name'] = self.instance.user.first_name
            self.initial['last_name'] = self.instance.user.last_name
        except User.DoesNotExist:
            pass
    email = forms.EmailField(label='Primary Email')
    first_name = forms.CharField(label='First name')
    last_name = forms.CharField(label='Last name')    
    unsubscribe = forms.BooleanField(label='Unsubscribe from NNS Emails', required=False)
    
    class Meta:
        model = UserProfile
        fields = ['first_name','last_name','email','unsubscribe']


    def save(self, *args, **kwargs):
        u = self.instance.user
        p = self.instance.user.get_profile()
        u.email = self.cleaned_data['email']
        u.first_name = self.cleaned_data['first_name']
        u.last_name = self.cleaned_data['last_name']
        if self.cleaned_data['unsubscribe']:
            p.user_type = 'InactiveClient'
        u.save()
        p.save()
        client = super(UnsubscribeForm, self).save(*args,**kwargs)
        return client
        
         
        
