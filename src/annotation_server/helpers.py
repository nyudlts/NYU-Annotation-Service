import sys
from decorator import decorator
from traceback import format_exception
import logging

from optparse import make_option, OptionParser
from django.core.management import call_command, setup_environ, color

from ConfigParser import (ConfigParser, NoSectionError, NoOptionError,
                          DuplicateSectionError)

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class PropertyStore(dict):
	'''
	This class wraps dict and add ability to add properties to himself with dot notation.
	>>> p = PropertyStore(a=1, b=2)
	>>> print p.a
	1
	>>> print p.b
	2
	>>> p.aa = 11
	>>> p.aa
	11
	>>> p.new_property = 'asdas'
	>>> p.new_property
	'asdas'
	'''
	def __setattr__(self, prop, val):
		self[prop] = val

	def __getattr__(self, prop):
		if prop in self:
			return self[prop]
		else:
			raise KeyError(prop)


class BaseCommand(object):
    option_list = (
        make_option('-v', '--verbosity',  action='store', dest='verbosity', default='1',
            type='choice', choices=['0', '1', '2', '3'],
            help='Verbosity level; 0=minimal output, 1=normal output, 2=all output'),
        make_option('--traceback', action='store_true',
            help='Print traceback on exception'),
        make_option('--with_logs', action='store_false', dest='with_logs', default=False,
                    help='Need logging?')
    )

    def __init__(self):
        """docstring for __init__"""
        self.style = color.color_style()

    def create_parser(self, prog_name):
        """
        Create and return the ``OptionParser`` which will be used to
        parse the arguments to this command.

        """
        return OptionParser(
			prog=prog_name,
			#usage=self.usage(subcommand),
			option_list=self.option_list
		)


    def execute(self, *args, **options):
        try:
            self.handle(*args, **options)
        except Exception as e:
            sys.stderr.write('ERROR: ' + unicode(e))
            sys.exit(1)

    def handle(self, *args, **opts):
        raise NotImplementedError("Not implemented yet")

    def __call__(self):
        # executing command
        argv = sys.argv if len(sys.argv) > 1 else sys.argv + ['', '']
        parser = self.create_parser(argv[0])
        options, args = parser.parse_args(argv[1:])
        #~ handle_default_options(options)
        self.execute(*args, **options.__dict__)


def get_traceback():
    return " ".join(format_exception(*sys.exc_info()))

@decorator
def trace_handler_error(f, *args, **kwargs):
    logit = lambda *a: log.info("trace_handler_error {}".format("".join([unicode(i) for i in a])))
    logit(args)
    logit(kwargs)
    try:
        return f(*args, **kwargs)
    except Exception as e:
        logit(e)
        logit(get_traceback()) #" ".join(format_exception(*sys.exc_info())))
        #raise e.__class__(unicode(e))

def get_config_var(config, section, var_name, default, config_path='./config.cfg'):
    '''
    This function recieves
        config as instance of ConfigReader
        section, var_name as string
        default is default value for this variable
    Type of returned variable will be the same as the type of default variable.
    '''
    try:
        mapper = {
            bool: config.getboolean,
            float: config.getfloat,
            int: config.getint,
        }
        return mapper.get(type(default), config.get)(section, var_name)
        #return config.get(section, var_name, default)
    except (NoSectionError, NoOptionError):
        try:
            config.add_section(section)
        except DuplicateSectionError:
            pass
        config.set(section, var_name, default)
        # writing our configuration file to 'check_installation.cfg'
        with open(config_path, 'wb') as configfile:
            config.write(configfile)
        return default


