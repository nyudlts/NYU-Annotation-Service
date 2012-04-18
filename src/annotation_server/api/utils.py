import types
import datetime
from decorator import decorator
from piston.utils import HttpResponse, rc
from django.utils import simplejson
from django.db import models
from django.shortcuts import _get_queryset
from xml2dict import fromstring as xml_fromstring
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import sys
import re
import logging
from django.conf import settings

class DecodeError(Exception):
    pass

class NotFoundError(Exception):
    pass


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def date_to_utc_format(model, *args, **kwargs):
    '''
    This decorator decorates class and adds to it properties
    which formats dates to UTC format.
    '''
    if not issubclass(model, models.Model):
        raise ValueError("Can not decorate instance wich isn't models.Model class")

    datetime_format = getattr(
        settings, "API_DATETIME_FORMAT", "%Y-%m-%dT%h:%MZ")

    def create_property(field_name):
        def _get_date_utc(self):
            return getattr(self, field_name).strftime(datetime_format)

        def _set_date_utc(self, val):
            if not isinstance(val, datetime.datetime):
                val = datetime.datetime.strptime(val, datetime_format)
            setattr(self, field_name, val)

        return property(_get_date_utc, _set_date_utc)

    for field in model._meta.fields:
        if isinstance(field, models.DateTimeField):
            setattr(model, "{0}_utc".format(field.name), create_property(field.name))

    return model


def create_logger(name, file_name, level, need_print=True):
    '''
    This function returns logger instance.
    Logger will log to the file and if need_print
    variable is setted up it will log to display to.
    '''
    log = logging.getLogger(name)
    log.setLevel(level)
    fh = logging.FileHandler(file_name)
    formatter = logging.Formatter(
        (
            '%(asctime)s - %(name)s - '
            '%(levelname)s - %(message)s'
        )
    )
    fh.setFormatter(formatter)
    log.addHandler(fh)

    if need_print:
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        log.addHandler(ch)
    return log



def map_fields(operation='POST', map_in={}, map_out={}):
    @decorator
    def wrap(f, self, request, *args, **kwargs):
        if map_in:
            data = getattr(request, operation)
            for k, v in map_in.items():
                if data.get(k, None):
                    data[v] = data.pop(k)
            setattr(request, operation, data)
        resp = f(self, request, *args, **kwargs)
        #if map_out:
            #compl_resp = {}
            #for k, m in map_out.items():
                #if hasattr(resp, k):
                    #setattr(resp, m, getattr(resp, k))
                    ##delattr(resp, k)

            #for k, v in resp.items():
                #if k in map_out:
                    #resp[map_out[k]] = resp.pop(k)
        return resp
    return wrap


def decode_from_string(content_type, string):
    '''
    This function recieves string and returns an object
    decoded from this string.
    These formats are can be decoded:
        JSON
        JSONP
        XML
    '''
    def jsonp_loader(json):
        reg = r'(?P<callback>\w+)\((?P<json>.*)\)'
        compile_obj = re.compile(reg,  re.DOTALL)
        match = compile_obj.search(json)
        if match:
            # it means that we are dealing with jsonp
            json = match.group('json')
        return simplejson.loads(json)

    data_loaders = {
        'text/xml': xml_fromstring,
        'application/json': simplejson.loads,
        'application/javascript': jsonp_loader,
    }

    if content_type not in data_loaders:
        raise DecodeError(
            ("Wrong data format or content type."
             "Content type should be one of {0}".format(
                 " ".join(data_loaders.keys()))
            )
        )
    return data_loaders[content_type](string)


def transform_request_payload(operation='POST', field_name='',
                              find_in_root=True):
    ''' This decorator transforms request data from string to XML or JSON
    and replace it into request. Recieves:
        @param operation: request type. It can be POST, PUT or GET.
        @param field_name: property name of the root data to find it into request.
        @param find_in_root: shout I find data in the root of the request?
    '''
    @decorator
    def wrap(f, self, request, *args, **kwargs):
        #from api.handlers import log
        c_type = request.content_type
        try:
            #data = data_loaders[c_type](request.raw_post_data)[field_name]
            data = decode_from_string(c_type, request.raw_post_data)[field_name]
        except KeyError as e:
            if find_in_root:
                data = decode_from_string(c_type, request.raw_post_data)
                #data = data_loaders[c_type](request.raw_post_data)
            else:
                raise e, sys.gettrace()
        setattr(request, operation, data)
        return f(self, request, *args, **kwargs)
    return wrap

login_required = method_decorator(login_required)

def add_fields_to_request(mapper={'response':
                                  {'numFound': ('response.__len__', (), int),
                                   'start': ('request.GET.get', ("start", 0), int),
                                   'includeDeletions': ('request.GET.get', ("includeDeletions", False), bool),
                                   'annotations': 'response'}}):
    '''
    This decorator can add some fields into response.
    Recieves a dict where dict's key would be a key in the response
    and dict's value would be value.
    There's convenience:
        Request and response are keywords in this scope.
        You can run some functions with parameters.
            In this case you should to pass tuple into dict's value
            with the parameters.
    Please think before what are you doing.
    '''
    @decorator
    def wrap(f, self, request, *args, **kwargs):
        def get_props(obj, str_, args=(), res_type=None):

            def get_or_call(obj, attr, f_args):
                '''
                obj - is any object
                attr - string
                '''
                if not attr:
                    return obj
                prop = getattr(obj, attr, None)
                if callable(prop):
                    return prop(*f_args)
                return prop
            # end get_or_call

            getter = (lambda obj, props:
                reduce(
                    lambda prev, attr: get_or_call(prev, attr, ()),
                    props, obj
                ))
            # end getter

            def run_last_func(obj, params, args):
                if args:
                    last = getter(obj, params[:-1])
                    return get_or_call(last, params[-1], args)
                return getter(obj, params)
            # end run_last_func

            spl = str_.split('.')[1:]
            if len(spl) > 1:
                result = run_last_func(obj, spl, args)
            else:
                result = get_or_call(obj, spl[0] if spl else "", args)
            if not result:
                not_res = {
                    int: 0,
                    str: "",
                    object: dict(),
                    dict: dict(),
                    list: list()
                    # add default values here for other types
                }
                result = not_res.get(res_type, None)

            return res_type(result) if res_type else result
        # end get_props
        try:
            response = f(self, request, *args, **kwargs)
        except NotFoundError as e:
            return rc.NOT_FOUND

        class Response(dict):
            def __init__(self, mapper={}, request=None, response=None):
                self.mapper = mapper
                self.request = request
                self.response = response


            def resolve_fields(self, map_):

                ret = {}

                for k, v in map_.items():
                    # Working on response:
                    # if string we just get this properties and return them.
                    if isinstance(v, basestring):
                        obj = getattr(self, v.split('.')[0], None)
                        ret[k] = get_props(obj, v)
                    if isinstance(v, (list, tuple)):
                        r_type = None
                        prop, args, r_type = (
                            v if len(v) == 3 else list(v)+[None])
                        if isinstance(r_type, (list, tuple)):
                            r_type = r_type[0]
                        obj = getattr(self, v[0].split('.')[0], None)
                        ret[k] = get_props(obj, prop, args, r_type)
                    if isinstance(v, dict):
                        # here is recursion
                        ret[k] = self.resolve_fields(v)
                return ret

        return Response(mapper, request, response).resolve_fields(mapper)

    # end wrap
    return wrap


def get_object_or_None(model_cls, **kwargs):
    try:
        return _get_queryset(model_cls).get(**kwargs)
    except model_cls.DoesNotExist:
        return None

