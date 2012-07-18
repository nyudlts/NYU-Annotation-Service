import datetime
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils import simplejson
import urllib2
from api.emiters import HTMLEmitter
from piston.emitters import Emitter
from .utils import date_to_utc_format
Emitter.register('html', HTMLEmitter, 'text/html; charset=utf-8')
from piston.utils import Mimer

Mimer.register(simplejson.loads, ('application/json', 'application/json; charset=UTF-8',))

class Profile(User):

    # Users profile should be implemented here.

    drupal_uid = models.CharField(blank=True, null=True, max_length=255)

class Constraint(models.Model):
    start = models.CharField(max_length=255)
    end = models.CharField(max_length=255)
    startOffset = models.IntegerField(default=0)
    endOffset = models.IntegerField(default=0)
    target = models.ManyToManyField('Target')
    annotation = models.ForeignKey('Annotation', related_name='constraints')

class Target(models.Model):
    url = models.URLField(verify_exists=False, max_length=255)

    def __unicode__(self):
        return self.url

class AnnotationsManager(models.Manager):
    def active(self, **kwargs):
        return self.get_query_set().exclude(~Q(deleted=False) & ~Q(has_answers=True)).filter(**kwargs)

    def inactive(self, **kwargs):
        return self.get_query_set().filter(Q(deleted=True) & Q(has_answers=False), **kwargs)


@date_to_utc_format # this decorator adds properties for each DateTime field in model
class Annotation(models.Model):
    
    TYPE_CHOICES = (
        ('Reply', 'Reply'),
        ('Rating', 'Rating'),
        ('Comment', 'Comment')
    )

    creation_date = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())
    modification_date = models.DateTimeField(auto_now=True, )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='Comment')
    author = models.ForeignKey(Profile)
    target = models.ManyToManyField(Target)
    body = models.TextField()
    private = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    has_answers = models.BooleanField(default=False)
    annotations = AnnotationsManager()
    objects = models.Manager()

    def get_creator(self):
        return self.author.drupal_uid or self.author.id

    def set_creator(self, auth_username):
        try:
            u = User.objects.get(username=auth_username)
            self.author = u
        except User.DoesNotExist as e:
            raise e

    creator = property(get_creator, set_creator)

    def get_constraints(self):
        return Constraint.objects.filter(annotation=self)

    def set_constraints(self, val):
        pass

    constraints = property(get_constraints)
    ranges = property(get_constraints)

    @property
    def text(self):
        return self.body if not self.deleted else ''

    @property
    def was_changed(self):
        # not used
        filter_date = lambda date: date.strftime("%Y %M %d %H %M %S")
        return filter_date(self.creation_date) != filter_date(self.modification_date)

    @property
    def url(self):
        return self.get_absolute_url()

    class Meta:
        verbose_name_plural = "Annotations"

    @models.permalink
    def get_absolute_url(self):
        return ('annotation_handler', None,
            {
                'annotation_id': str(self.id),
                'emitter_format':'json',
                'creator_id': (self.author.drupal_uid or self.author.id),
            }
        )

    def __unicode__(self):
        return "Annotation {0}".format(self.id)

    def _get_json_info(self):
        int_fields = ('nid', 'pages_count',)
        data = simplejson.loads(urllib2.urlopen("{0}/metadata".format(self.target.path)).read())
        for k, v in data.items():
            if k in int_fields:
                data[k] = int(v)
        return data

    def save(self):
        return super(Annotation, self).save()