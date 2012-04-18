#import logging

#log = logging.getLogger(__name__)

class ContentTypeMiddleware(object):
    def process_request(self, request):
        #log.info("----> PROCESS REQUEST")
        ctype = request.META.get('CONTENT_TYPE', '')
        #log.info(ctype)
        if ctype and ';' in ctype and not ctype.startswith('multipart/'):
            #log.info("------> Changing content type in request")
            request.META['CONTENT_TYPE'] = ctype.split(';')[0].rstrip()
        else:
            pass
            #log.info("----> Doesn't change content type")
        #log.info("End of middleware")
