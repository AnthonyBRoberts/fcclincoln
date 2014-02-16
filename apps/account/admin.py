from django.contrib import admin
from django.contrib.admin import site, ModelAdmin, SimpleListFilter
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from models import *


class UserTypeFilter(SimpleListFilter):
    title = 'User Type'
    parameter_name = 'user_type'

    def lookups(self, request, model_admin):
        usertypes = set([c.user_type for c in UserProfile.objects.all()])
        return [(c, c) for c in usertypes]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(userprofile__user_type=self.value())
        else:
            return queryset


class PubTypeFilter(SimpleListFilter):
    title = 'Pub Type'
    parameter_name = 'pub_type'

    def lookups(self, request, model_admin):
        pubtypes = set([c.pub_type for c in UserProfile.objects.all()])
        return [(c, c) for c in pubtypes]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(userprofile__pub_type=self.value())
        else:
            return queryset


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'user profiles'
    list_filter = ('user_type', )
    fieldsets = (
        ('Staff information', {
            'fields': (('user_type', 'can_publish'), 'byline', 'bio'),
        }),
        ('Client information', {
            'classes': ('collapse',),
            'fields': (('pub_name', 'pub_type'),
                       'pub_area', 'phone', 'address', 'city',
                       'state', 'zipcode', 'website',
                       ('facebook', 'twitter'), 'about'),
        }),
    )


class UserAdmin(UserAdmin):
    list_display = ('get_pub_name', 'get_pub_type', 'email', 'first_name', 'last_name', 'get_user_type', 'is_staff', )
    list_display_links = ('get_pub_name', 'get_pub_type', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_type',)
    list_filter = ('is_staff', UserTypeFilter, PubTypeFilter, )
    search_fields = ['email', 'first_name', 'last_name', 
                    'userprofile__pub_name', 'userprofile__about', 'userprofile__user_type',]


    def get_user_type(self, user):
        return ('%s' % user.get_profile().user_type)
    get_user_type.short_description = "User Type"
    get_user_type.admin_order_field = "userprofile__user_type"

    def get_pub_name(self, user):
        return ('%s' % user.get_profile().pub_name)
    get_pub_name.short_description = "News Organization Name"
    get_pub_name.admin_order_field = "userprofile__pub_name"

    def get_pub_type(self, user):
        return ('%s' % user.get_profile().pub_type)
    get_pub_type.short_description = "News Organization Type"
    get_pub_type.admin_order_field = "userprofile__pub_type"

    inlines = (UserProfileInline, )
    
    
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

