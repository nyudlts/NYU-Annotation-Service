import datetime
import sys, os
import copy
from piston.handler import BaseHandler
from piston.resource import rc
from piston.utils import validate, require_mime

from models import *
from forms import AnnotationForm, ConstraintForm

from django.utils import simplejson
from django.db.models import Q
from django.conf import settings
from django.db.models import Count
from django.contrib.auth.decorators import login_required

import re
from xml2dict import fromstring

import logging

from helpers import trace_handler_error, get_traceback

from api.utils import (
    login_required, map_fields, add_fields_to_request,
     get_object_or_None, NotFoundError,
    transform_request_payload
)


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class AnnotationHandler(BaseHandler):
    '''
    This handler handles annotations.
    This handler processes the annotations.
    Creates a new, removes and returns the list of existing annotations.
    '''
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = Annotation

    csrf_exempt = True

    fields = (
        'id',
        ('creator'),
        #'body',
        'type',
        ('target', ('url',)),
        'coordinates',
        'creation_date_utc',
        'url',
        'private',
        'deleted',
        'modification_date_utc',
        ('ranges', ('start', 'end', 'startOffset', 'endOffset')),
        'text', 'quote',
    )

    fake_username = lambda self, uid: (
        getattr(settings, 'FAKE_USERNAME', '') + unicode(uid)
    )

    mapper={'numFound': ('response.__len__', (), int),
            'start': ('request.GET.get', ("start", 0), int),
            'includeDeletions': ('request.GET.get', ("includeDeletions", False), bool),
            'annotations': ('response', (), list),
           }

    @add_fields_to_request({'response':  mapper})
    def read(self, request, creator_id=None, annotation_id=None, *args, **kwargs):
        #log.info("read handler works {0}".format(log.name))
        '''
        This method works only when the GET request sended to the server.

        Returns a list of annotations.
        GET parameters can be:

        oldest = oldest item to return (CCYY-MM-DDThh:mm:ssZ);

        newest = newest item to return (CCYY-MM-DDThh:mm:ssZ);

        start = first item to return (INT);

        limit = how much items will be returned (INT);

        targetUri = URI for a target (URI);

        ###### Not implemented yet

        withInlineContent = whether or not to return inline body content (TRUE or FALSE; default = TRUE).
        '''

        def create_date(s):
            reg = (r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})'
                  'T(?P<hour>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2})Z')
            match = re.match(reg, s)

            mch = lambda d: int(match.group(d))
            return datetime.datetime(
                year=mch('year'),
                month=mch('month'),
                day=mch('day'),
                hour=mch('hour'),
                minute=mch('minutes')
            )

        includeDeletions = (
            True if request.GET.get('includeDeletions', 0) == "true"
            else False)
        active = Annotation.annotations.active()
        annotations = (active if includeDeletions
                           else active.filter(deleted=False))



        def filter_by_creator_id(request, qs, creator_id):
            ''' This function recievs queryset and creator id.
            Returns updated queryset, filtered by creator id'''

            if request.user.is_authenticated():
                # exclude from queryset annotations which are private
                # and are not owned by registered user
                qs = qs.exclude(~Q(author=request.user), private=True)
            else:
                # if user is not logged in exclude all private annotations
                qs = qs.exclude(private=True)

            # NOTE: Django user id has low priority before drupal user id
            if creator_id:
                user = (get_object_or_None(Profile, username=self.fake_username(creator_id))
                        or get_object_or_None(Profile, id=creator_id))
                if not user:
                    raise NotFoundError('User not found')

                ((log.info("FOUND DRUPAL USER")
                 if user.drupal_uid else log.info("FOUND DJANGO USER"))
                 if user else log.info("NO USER FOUND"))
                qs = qs.filter(author=user) if user else qs
            return qs


        def filter_by_annotation_id(request, qs, annotation_id, filtered_by_creator=False, creator_id=None):
            '''This function recieves queryset filtered by user and
            filters it by anntation id.'''
            if not annotation_id:
                return qs

            if not filtered_by_creator and creator_id:
                qs = filter_by_creator_id(request, qs, creator_id)

            kw = dict(
                id=annotation_id,
                #deleted=includeDeletions,
            )
            if includeDeletions:
                kw.setdefault('deleted', True)

            if bool(request.GET.get('nested', False)):
                annotation= qs.get(**kw)
                return qs.filter(
                    target__url__in=[t.url for t in annotation.target.all()],
                    has_answers=False,
                    deleted=True if includeDeletions else False
                ).exclude(id=annotation.id)
            return qs.filter(**kw)


        def filter_by_constraint(request, qs):
            '''This funcion filters annotations by:
                date
                    oldest
                    newest
                targetUri
            Do slice of queryset:
                start
                limit
            '''
            constraints = {
                'oldest': lambda v: ('creation_date__lte', create_date(v)),
                'newest': lambda v: ('creation_date__gte', create_date(v)),
                'targetUri': lambda v: ('target__url__icontains', v),
            }
                #'withInlineContent')
            q = dict(q_rep(request.GET.get(con))
                      for con, q_rep in constraints.items()
                      if con in request.GET)
            if q:
                qs = qs.filter(**q)
            return qs


        def filter_by_limit(request, qs):
            try:
                start = int(request.GET.get('start', 0))
                limit = int(request.GET.get('limit', request.GET.get('rows', 50)))
                end = start + limit
            except ValueError:
                log.error(("Can not convert arguments start and stop "
                           "to int. start={0} and stop={1}".format(start, stop)))
                start = 0
                end = 50
            return qs.order_by('creation_date')[start: end]


        def inGET(name):
            return name in request.GET

        try:
            if creator_id:
                annotations = filter_by_creator_id(request, annotations, creator_id)

            if annotation_id:
                annotations = filter_by_annotation_id(request, annotations, annotation_id)

            return filter_by_limit(request, annotations)
            #return delete_content_from_deleted_annots(request, limited)

        except NotFoundError as e:
            log.info(u"Error in AnnotationHandler.read(). Error was "+get_traceback())
            raise e
        except Exception as e:
            log.info(u"Error in AnnotationHandler.read(). Error was "+get_traceback())
            raise e

    #@trace_handler_error
    #@login_required
    @require_mime('xml', 'json')
    @transform_request_payload(field_name='annotation')
    @map_fields('POST', map_in={'text': 'body'})
    # NOTE: this decorator replaces field "text" into POST payload with field named "body" with the same content.
    @validate(AnnotationForm, 'POST')
    def create(self, request, creator_id, **kwargs):
        '''
        This method works only when POST request sended to the server.

        Creates new annotation.
        This function should takes JSON or XML.

        Recieved XML or json should contains fields: 'body', 'type', 'target'
        and may contain field 'ranges' which would be saved as 'constraints' field in
        new annotation.
        '''


        def get_user(request, creator=None):
            log.info("get_or_create_user FUNC")
            if creator and request.user.is_anonymous():
                log.info("ID is {0} and user is anonymous".format(creator_id))
                return Profile.objects.get_or_create(
                    drupal_uid=creator,
                    username=self.fake_username(creator)
                )[0]
            elif request.user.is_authenticated():
                log.info("User is Authenticated")
                return request.user
            else:
                log.info("ERROR fully anonymously user")
                return {
                    'error': ("Can not create annotation with fully "
                              "annonymous user. Please login or provide drupal_uid.")}

        def save_constraints(request, annotation, field_name='ranges'):
            '''
            This function saves constraints and returns saved constraints instances.
            argument "field_name" define where ocnstraints are locate in request.POST
            '''
            if field_name in request.POST:
                print "savin' constraints {0}".format(
                    request.POST.get(field_name, "No ranges in request.POST")
                )
                def save_one(data):
                    # save constraints if exists
                    form = ConstraintForm(data)
                    if form.is_valid():
                        const = form.save(commit=False)
                        const.annotation = annotation
                        const.save()
                        const.target = annotation.target.all()
                        return const
                    else:
                        return
                return [save_one(i)
                        for i in request.POST[field_name]
                        if isinstance(i, dict)
                       ]

        try:
            creator_id = get_user(request, creator_id)
            annotation = request.form.save(commit=False)
            annotation.author = creator_id
            annotation.private = (
                0 if creator_id.drupal_uid
                else request.form.cleaned_data['private'])
            annotation.save()
            request.form.save_m2m()

            constraints = save_constraints(request, annotation)

            qs = Annotation.objects.filter(
                target__url__in=[t.url for t in annotation.target.all()],
                has_answers=False,
                deleted=False
            ).exclude(id=annotation.id)

            if annotation.type == "Reply" and qs.count():
                qs.update(has_answers=True)
            return annotation
        except Exception as e:
            log.error("Errow while creating new one annotation. Error was {0}, traceback: {1}".format(e, get_traceback()))
            return e

    @login_required
    @require_mime('xml', 'json')
    @transform_request_payload(operation='PUT', field_name='annotation')
    @map_fields('PUT', map_in={'text': 'body'})
    @validate(AnnotationForm, 'PUT')
    def update(self, request, creator_id, annotation_id, **kwargs):
        '''
        This function updates annotation. Annotation instance should have id.
        '''
        try:
            #instance = Annotation.objects.get(id=request.form.cleaned_data['id'])
            instance = Annotation.annotations.active().get(
                id=annotation_id, author__id=creator_id
            )
            form = AnnotationForm(request.PUT, instance=instance)
            if form.is_valid():
                return form.save()
            return form
        except Annotation.DoesNotExist as e:
            return rc.NOT_FOUND
    @trace_handler_error
    @login_required
    def delete(self, request, creator_id, annotation_id=None, **kwargs):
        '''
        This method works only when the DELETE request sended to the server.

        Delete annotation. Recieves creator's username and request should contain target with targetUri and annotation.id in the GET

        For example: DELETE /api/annotations/admin/?id=122&target=http://bla.bla/sdfs
        '''
        id = annotation_id or request.GET.get('id', 0)
        target = request.GET.get('target', '')

        log.info("=== DELETE HANDLER ====")

        log.info(request.user)

        #is_owner = request.user.username == creator_id
        if (request.user.is_authenticated() and annotation_id):
            try:
                qkw = {
                    'author': request.user,
                    'id': id
                }
                if target:
                    qkw.setdefault('target__url', target)

                print "**"*10, qkw
                print "============== Count in handler ", [(i.id, i.author) for i in Annotation.annotations.active()]
                annot = Annotation.annotations.active().get(**qkw)
                print "_+_+"*20, annot
                # delete annotation ( mark as deleted )

                log.info("ANNOT.URL {0}".format(annot.url))

                replies = Annotation.annotations.active(target__url__endswith=annot.url)

                log.info("Replies {0}".format(replies))

                annot.has_answers = bool(replies.count())
                annot.deleted=True
                annot.deleted_at=datetime.datetime.now()
                annot.save()

                q = Annotation.annotations.active(target__url__in=[i.url for i in annot.target.all()])

                log.info([i.url for i in annot.target.all()])
                log.info("q = {0}".format(q))
                log.info("q.count() = {0}".format(q.count()))

                if q.count() <= 1:
                    "this is a last answer or annotation with the same target"
                    q.update(has_answers=False)

                return rc.DELETED

            except (Annotation.MultipleObjectsReturned, Annotation.DoesNotExist) as e:
                log.info("BAD REQUEST exception raised")
                return rc.BAD_REQUEST
        else:
            print "KWARGS = ", kwargs


class StatusHandler(BaseHandler):
    methods = ('GET',)

    def read(self, request):
        handler = AnnotationHandler()
        for method in request:
            pass
        return {'status': 'ok'}
