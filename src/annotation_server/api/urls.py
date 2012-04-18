from django.conf.urls.defaults import *
from piston.resource import Resource
from api.handlers import AnnotationHandler
from piston.doc import documentation_view

class CsrfExemptResource(Resource):
    """A Custom Resource that is csrf exempt"""
    def __init__(self, handler, authentication=None):
        super(CsrfExemptResource, self).__init__(handler, authentication)
        self.csrf_exempt = getattr(self.handler, 'csrf_exempt', True)

annotation_handler = CsrfExemptResource(AnnotationHandler)

emitter_formats = "|".join(
    ["(?:{0})".format(i) for i in ['xml', 'json']]
)

urlpatterns = patterns('',
    url(r'^annotations(?:\/(?P<creator_id>\w+))?(?:\/(?P<annotation_id>\d+))?(?:\.(?P<emitter_format>'+emitter_formats+'))?$',
    #url(r'^annotations(?:\/(?P<creator>\w+))?(?:\.(?P<emitter_format>'+emitter_formats+'))?(?:\/(?P<id>\d+))?$',
        annotation_handler,
       name='annotation_handler'),

    # automated documentation
    url(r'^documentation/?$', documentation_view),
)

