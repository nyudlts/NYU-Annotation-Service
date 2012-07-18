from django.conf.urls.defaults import *
from piston.resource import Resource
from api.handlers import AnnotationHandler

class CsrfExemptResource(Resource):
    def __init__(self, handler, authentication=None):
        super(CsrfExemptResource, self).__init__(handler, authentication)
        self.csrf_exempt = getattr(self.handler, 'csrf_exempt', True)

annotation_handler = CsrfExemptResource(AnnotationHandler)

emitter_formats = "|".join(["(?:{0})".format(i) for i in ['xml', 'json']])

urlpatterns = patterns('',
    url(
        r'^annotations(?:\/(?P<creator_id>\w+))?(?:\/(?P<annotation_id>\d+))?(?:\.(?P<emitter_format>'+emitter_formats+'))?$',
        annotation_handler, 
        name='annotation_handler'
    ),
)