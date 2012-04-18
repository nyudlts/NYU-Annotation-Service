from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('profile.views',
    url(r'^(?P<creator>\w+)?$', 'profile',
       name='profile'),
)
