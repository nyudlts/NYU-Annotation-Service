# Create your views here.

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.auth.models import User
from django.views.generic.simple import direct_to_template
from api.forms import TestForm
from api.models import Annotation, Profile
from django.db.models import Q
from api.utils import get_object_or_None

def profile(request, creator):
    if creator:
        creator = get_object_or_None(Profile, username=creator)

        if not creator:
            return direct_to_template(
                request,
                'profile/does_not_exists.html',
                {
                    'username': creator,
                    'all_users': Profile.objects.all()
                }
            )
    else:
        creator = request.user

    annots = Annotation.objects.filter(
        author=creator,
        deleted=False,
    )
    if request.user.is_authenticated():
        annots = annots.exclude(~Q(author=request.user), private=True)

    return direct_to_template(
        request,
        'profile/profile.html',
        {
            'annotations': annots.filter(type='Comment'),
            'replies': annots.filter(type='Reply'),
            'creator': creator,
            'all_users': User.objects.all()

        }
    )
