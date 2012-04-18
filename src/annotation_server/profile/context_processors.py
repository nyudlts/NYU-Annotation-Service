from django.contrib.sites.models import Site, RequestSite

def current_site(request):
    if Site._meta.installed:
        current_site = Site.objects.get_current()
    else:
        current_site = RequestSite(request)

    return {'current_site': current_site}
