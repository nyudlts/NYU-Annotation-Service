"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import urllib
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from nose.tools import eq_, raises
from django.utils import simplejson
from nose.plugins.attrib import attr
import re
from pprint import pprint
from decorator import decorator
from django.db.models import Avg, Max, Min
from django.conf import settings
from django.utils.encoding import smart_str
from django.utils.http import urlencode

from api.models import Annotation, Target, User, Profile


@decorator
def make_annotations_independent(func, self):
    # setting up data
    f_old_start, self.first_annotation['response']['start'] = (
        self.first_annotation['response']['start'], 0)
    s_old_start, self.second_annotation['response']['start'] = (
        self.second_annotation['response']['start'], 0)
    r = func(self)
    # setting up backuped data
    self.first_annotation['response']['start'] = f_old_start
    self.second_annotation['response']['start'] = s_old_start

    return r


def eq_json(a, b):
    '''
    compare 2 dicts recursively
    '''
    import time
    if a == b:
        return True
    for k, v in a.items():
        if a.get(k, time.time()) != b.get(k, time.time()):
            if isinstance(a[k], dict):
                return eq_json(a[k], b[k])
            elif isinstance(a[k], (tuple, list)):
                for i in xrange(len(a[k])):
                    if isinstance(a[k][i-1], dict) and isinstance(b[k][i-1], dict):
                        try:
                            eq_json(a[k][i-1], b[k][i-1])
                        except IndexError as e:
                            print "\n\n\n ERROR, index i=", i

                            pprint(a[k][i-1])
                            pprint(b[k][i-1])
                            print "\n\n\n"
                            raise e
                    elif a[k][i] == b[k][i]:
                        continue
                    else:
                        pprint(a[k][i])
                        print "!="
                        pprint(b[k][i])
                        print "\n\n"
                        assert a[k][i]==b[k][i]
            else:
                print "Different field: {0}".format(k)
                pprint(a[k])
                print type(a[k])
                print "!="
                pprint(b[k])
                print type(b[k])
                print "\n\n"

    if not a==b:
        pprint(a)
        print "!="
        pprint (b)
        print type(a)
        print type(b)




class AnnotationHandlerTest(TestCase):
    api_client = Client()

    fixtures = ['test_data.json',]

    user = 'admin'
    password = 'admin'

    def _get_annotations(self, emitter_format="json", need_login=True, **kwargs):
        emitter_format = emitter_format.lower()

        def json_loader(json):
            reg = r'(?P<callback>\w+)\((?P<json>.*)\)'
            compile_obj = re.compile(reg,  re.DOTALL)
            match = compile_obj.search(json)
            if match:
                # it means that we are dealing with jsonp
                assert kwargs.get('callback', '') == match.group('callback'), "Callback function does not match"
                json = match.group('json')
            return simplejson.loads(json)

        format_loaders =  dict([
            ("json", json_loader),
            ("xml", lambda *s: None),
            ("jsonp", json_loader),
        ])

        if emitter_format not in format_loaders:
            raise TypeError("You can get response only in json, jsonp "
                            "or xml format.")
        if need_login:
            assert self.api_client.login(username='admin', password='admin'), "Can not login"

        if emitter_format == 'jsonp':
            emitter_format = emitter_format[:-1]

        rev_kw = {'emitter_format': emitter_format}

        creator_id = kwargs.get('creator_id', '')
        rev_kw.setdefault('creator_id', creator_id) if creator_id else ''

        url = reverse('annotation_handler', kwargs=rev_kw)
        if emitter_format == 'jsonp':
            url += "?callback=callback"

        response = self.api_client.get(url, kwargs)

        eq_(response.status_code, 200)

        return format_loaders[emitter_format](response.content)

    all_annotations = simplejson.loads('''
        {
        "response": {
            "start": 0,
            "numFound": 2,
            "includeDeletions": false,
            "annotations": [
                {
                    "target": [
                        {
                            "url": "http://dlib.nyu.edu/awdl/books/derportrtkopfd00borc"
                        }
                    ],
                    "modification_date_utc": "2011-10-03T13:13Z",
                    "creator": 1,
                    "deleted": false,
                    "text": "Annotation body",
                    "private": true,
                    "creation_date_utc": "2011-10-03T13:13Z",
                    "url": "/api/annotations/1/16.json",
                    "type": "Comment",
                    "id": 16
                },
                {
                    "target": [
                        {
                            "url": "http://dlib.nyu.edu/awdl/books/derportrtkopfd00borc/5"
                        }
                    ],
                    "modification_date_utc": "2011-10-04T13:13Z",
                    "creator": 1,
                    "deleted": false,
                    "text": "Annotation body",
                    "private": true,
                    "creation_date_utc": "2011-10-04T13:13Z",
                    "url": "/api/annotations/1/17.json",
                    "type": "Comment",
                    "id": 17
                }
            ]
        }
    }
    ''')
    first_annotation = simplejson.loads('''
        {
    "response": {
        "start": 0,
        "numFound": 1,
        "includeDeletions": false,
        "annotations": [
            {
                "target": [
                    {
                        "url": "http://dlib.nyu.edu/awdl/books/derportrtkopfd00borc"
                    }
                ],
                "modification_date_utc": "2011-10-03T13:13Z",
                "creator": 1,
                "deleted": false,
                "text": "Annotation body",
                "private": true,
                "creation_date_utc": "2011-10-03T13:13Z",
                "url": "/api/annotations/1/16.json",
                "type": "Comment",
                "id": 16
            }
        ]
    }
}
       ''')
    second_annotation = simplejson.loads('''
        {
    "response": {
        "start": 1,
        "numFound": 1,
        "includeDeletions": false,
        "annotations": [
            {
                "target": [
                    {
                        "url": "http://dlib.nyu.edu/awdl/books/derportrtkopfd00borc/5"
                    }
                ],
                "modification_date_utc": "2011-10-04T13:13Z",
                "creator": 1,
                "deleted": false,
                "text": "Annotation body",
                "private": true,
                "creation_date_utc": "2011-10-04T13:13Z",
                "url": "/api/annotations/1/17.json",
                "type": "Comment",
                "id": 17
            }
        ]
    }
}
    ''')

    @attr('fixtures', fixtures=1)
    def test_fixtures(self):
        from .models import Annotation, Target, Constraint
        from django.contrib.auth.models import User


        print "Users count "+str(User.objects.count())
        print "Profiles count "+str(Profile.objects.count())

        eq_(Annotation.objects.count(), 2)
        eq_(Profile.objects.count(), 1)
        print [p.username for p in Profile.objects.all()]
        p = Profile.objects.get(username='admin')
        print p.check_password('admin')
        eq_(Target.objects.count(), 5)
        eq_(Constraint.objects.count(), 0)

    @attr('read_all', read=1)
    def test_get_all_annotations_json(self):
   # test get all annotations
        annotations = self._get_annotations(emitter_format='json')
        eq_json(annotations, self.all_annotations)
        # these two lines are equal for JSON
        #eq_(annotations, self.all_annotations)

    # test get slice
    @attr('read_slice', read=1)
    def test_get_slice(self):
        # test get 1-st annotation
        eq_json(
            self._get_annotations(emitter_format='json', start=0, limit=1),
            self.first_annotation)

        # test get 2-nd annotation
        eq_json(
            self._get_annotations(emitter_format='json', start=1, limit=1),
            self.second_annotation)


    @attr('read_filter_user', read=1)
    def test_filter_by_user(self):
        u = Profile.objects.get(username='admin')
        annots = Annotation.objects.filter(author=u)
        eq_(annots.count(), len(self.all_annotations['response']['annotations']))
        # test get annotations filtered by user
        eq_json(self._get_annotations(emitter_format='json', start=0, limit=1, creator_id=u.id),
            self.first_annotation)

        #none_ann = self._get_annotations(emitter_format='json', start=0, limit=1, creator_id='100500')
        #assert none_ann != self.first_annotation, "Filter by user doesn't works! \n {0} \n != \n {1}".format(none_ann, self.first_annotation)
        #assert len(none_ann['response']['annotations']) == 0, "Len of response filtered by FAKE user is not zero!"

    @attr('read_filter_uri', read=1)
    def test_filter_by_uri(self):
        # test get annotation filtered by target URI
        annotation = simplejson.loads('''
        {
            "response": {
                "start": 0,
                "numFound": 1,
                "includeDeletions": false,
                "annotations": [
                    {
                        "target": [
                            {
                                "url": "http://dlib.nyu.edu/awdl/books/derportrtkopfd00borc/5"
                            }
                        ],
                        "creation_date_utc": "2011-10-04T13:13Z",
                        "modification_date_utc": "2011-10-04T13:13Z",
                        "creator":  1,
                        "deleted": false,
                        "text": "Annotation body",
                        "private": true,
                        "url": "/api/annotations/1/17.json",
                        "type": "Comment",
                        "id": 17
                    }
                ]
            }
        }
        ''')
        eq_json(self._get_annotations(
                emitter_format='json',
                targetUri="http://dlib.nyu.edu/awdl/books/derportrtkopfd00borc/5"),
            annotation)

    @attr('oldest', read=1)
    @make_annotations_independent
    def test_filter_by_date_newest(self):
        pprint(self.first_annotation)
        eq_json(self._get_annotations(
            emitter_format='json',
            oldest='2011-10-03T13:14:00Z'),
            self.first_annotation)

    @attr('read_newest', read=1)
    @make_annotations_independent
    def test_filter_by_date_oldest(self):
        eq_json(self._get_annotations(
            emitter_format='json',
            newest='2011-10-03T13:14:00Z'),
            self.second_annotation)

    def create_new_annotation(self, creator_id=1, json=None):
        '''
        This function creates new one annotation and returns decoded response
        and object related to it from DB.
        '''
        json = json or '''
        {
        "annotation":
            {
            "text": "Annotation body TEST",
            "type": "Comment",
            "target": [
                    {"url": "http://dlib.nyu.edu/awdl/books/derportrtkopfd00borc/test"}
                ]
            }
        }
        '''
        annots = list(Annotation.objects.all())

        url = reverse('annotation_handler', kwargs={'creator_id': creator_id})
        self.api_client.login(username='admin', password='admin')

        resp = self.api_client.post(
            url,
            data=json,
            content_type="application/json; charset=UTF-8",
        )
        eq_(resp.status_code, 200)
        eq_(len(annots), Annotation.objects.count()-1)
        pprint(resp.content)
        #assert False
        jresp = simplejson.loads(resp.content)#['response']['annotations'][0]
        return jresp, Annotation.objects.get(id=jresp['id'])



    @attr('create', create=1)
    def test_create_annotation(self):
        jannot, annot = self.create_new_annotation()
        assert isinstance(jannot, dict)
        # in response should be only dict and it should be only one
        eq_json(
            jannot,
            self._get_annotations(
                emitter_format='json',
                creator_id=1,
                annotation_id=annot.id
            )['response']['annotations'][0]
        )
        #assert False

    @attr('delete', delete=1)
    def test_delete_annotation(self):
        jannot, annot = self.create_new_annotation()
        url = reverse('annotation_handler',
                      kwargs=dict(creator_id=1,
                                  annotation_id=annot.id)
                     )
        resp = self.api_client.delete(
            url,
        )
        eq_(resp.status_code, 204)
        try:
            Annotation.annotations.active().get(id=annot.id)
            assert False, "Annotation does not deleted!!"
        except Annotation.DoesNotExist:
            pass

    @attr('update', update=1)
    def test_update_annotation(self):
        annot = Annotation.annotations.active()[0]
        self.api_client.login(username='admin', password='admin')
        url = reverse('annotation_handler',
                      kwargs=dict(creator_id=1,
                                 annotation_id=annot.id)
                     )
        data='''
            {"annotation":
                {
                "text": "Annotation body TEST updated",
                "type": "Comment",
                "target": [
                    {"url": "http://dlib.nyu.edu/awdl/books/derportrtkopfd00borc/test"}
                    ]
                }
            }'''
        resp = self.api_client.put(
            url,
            data=data,
            content_type="application/json; charset=UTF-8",
        )
        eq_(resp.status_code, 200)
        eq_(
            simplejson.loads(resp.content)['text'],
            simplejson.loads(data)['annotation']['text'],
        )
        eq_(
            Annotation.annotations.active().get(id=annot.id).text,
            "Annotation body TEST updated"
        )

    def test_get_annotations_jsonp(self):
        self._get_annotations(emitter_format='jsonp', content_type='application/javascript')

    @attr('constr', constr=1)
    def test_create_constraints(self):
        json = '''
        {
        "annotation":
            {
            "text": "Annotation body TEST",
            "type": "Comment",
            "target": [
                    {"url": "http://dlib.nyu.edu/awdl/books/derportrtkopfd00borc/test"}
                ],
            "ranges": [
                    {
                        "start": "testStart",
                        "end": "testEnd",
                        "startOffset": 0,
                        "endOffset": 11
                    }
                ]
            }
        }
        '''
        jannot, annot = self.create_new_annotation(creator_id=1, json=json)
        assert annot.constraints.count() == 1


    @attr('constr_many', constr=1)
    def test_create_many_constraints(self):
        json = '''
        {
        "annotation":
            {
            "text": "Annotation body TEST",
            "type": "Comment",
            "target": [
                    {"url": "http://dlib.nyu.edu/awdl/books/derportrtkopfd00borc/test"}
                ],
            "ranges": [
                    {
                        "start": "testStart1",
                        "end": "testEnd1",
                        "startOffset": 1,
                        "endOffset": 11
                    },
                    {
                        "start": "testStart2",
                        "end": "testEnd2",
                        "startOffset": 2,
                        "endOffset": 12
                    },
                    {
                        "start": "testStart3",
                        "end": "testEnd3",
                        "startOffset": 3,
                        "endOffset": 13
                    },
                    {
                        "start": "testStart4",
                        "end": "testEnd4",
                        "startOffset": 4,
                        "endOffset": 14
                    }
                ]
            }
        }
        '''
        jannot, annot = self.create_new_annotation(creator_id=1, json=json)
        assert annot.constraints.count() == 4
