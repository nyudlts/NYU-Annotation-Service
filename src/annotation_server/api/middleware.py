class ContentTypeMiddleware(object):
    def process_request(self, request):
        ctype = request.META.get('CONTENT_TYPE', '')
        if ctype and ';' in ctype and not ctype.startswith('multipart/'):
            request.META['CONTENT_TYPE'] = ctype.split(';')[0].rstrip()
        else:
            pass