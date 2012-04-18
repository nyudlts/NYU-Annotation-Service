from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from api.forms import TestForm
from piston.resource import Resource
from api.handlers import StatusHandler

admin.autodiscover()

application = patterns('',
    url(r'^api/', include('api.urls')),

    # django-registration enable
    url(r'^accounts/', include('registration.urls')),

    url(r'^annotations/', include('profile.urls')),

    # The next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^test_uc1/$', direct_to_template,
        {
            'template': 'openurl.annon.html'
        }, name='test_uc1'
       ),
    url(r'test_uc3/$', direct_to_template,
        {
            'template': 'text_annon.html'
        },
        name='test_uc3'
       ),
    #url(r'shib/', include('django_shibboleth.urls')),

    url(r'^$', direct_to_template,
        {
            'template': 'test.html',
            'extra_context': {'form': TestForm()},
        }, name="index"
    ),

    url(r'^status/?$', Resource(StatusHandler)),


)

urlpatterns = patterns('',
    url(r'^', include(application)),
)

# serving media files
urlpatterns += patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
       'document_root': settings.MEDIA_ROOT,
        'show_indexes': True,
   })
)
