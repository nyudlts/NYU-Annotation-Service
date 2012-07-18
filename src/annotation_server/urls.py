from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from api.forms import TestForm
from piston.resource import Resource
from api.handlers import StatusHandler

admin.autodiscover()

application = patterns('',
                       
    url(r'^$', direct_to_template, { 'template': 'index.html', }, name='index'),
    
    url(r'^api/', include('api.urls')),
        
    url(r'^annotations/', include('profile.urls')),
    
    url(r'^accounts/', include('registration.urls')),
    
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', include('profile.urls'), name="index"),
    
    url(r'^status/?$', Resource(StatusHandler)),

)

urlpatterns = patterns('', url(r'^', include(application)), )

# Media
urlpatterns += patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
       'document_root': settings.MEDIA_ROOT,
       'show_indexes': True,
   })
)