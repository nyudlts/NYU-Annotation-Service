# coding: utf-8
import logging
import time
import os
import sys
from subprocess import Popen, PIPE
from ConfigParser import ConfigParser, NoSectionError, NoOptionError, DuplicateSectionError
from helpers import BaseCommand, get_config_var, trace_handler_error, PropertyStore

build_path_to_local_file = lambda name: os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), name) #'check_install_error.log')
)

def exit_if_result(result_obj):
    if result_obj.returncode:
        sys.exit(1)


class CheckInstall(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(CheckInstall, self).__init__(*args, **kwargs)
        self._setup_configs()
        self.create_loggers()

    config = PropertyStore(
        config_vars = PropertyStore(**{
            'PORT': 8000,
            'HOST': '127.0.0.1'
        })
    )
    '''
    ==============================
    Commands
    '''
    CONFIG_FILE_PATH = 'check_install.cfg'
    VIRT_ENV = False

    '''
    ===============================
    Creating new config parser instance and reading config file.
    '''

    def _setup_configs(self):
        self._config = ConfigParser()
        self._config.read(self.CONFIG_FILE_PATH)


        self.config.error_log_path = get_config_var(
            self._config, 'Logs', 'error_log_path',
            build_path_to_local_file('check_install_error.log'),
            build_path_to_local_file('check_install.cfg')
        )
        self.config.info_log_path = get_config_var(
            self._config, 'Logs', 'info_log_path',
            build_path_to_local_file('check_install_info.log'),
            build_path_to_local_file('check_install.cfg')
        )
        self.config.need_print = get_config_var(
            self._config,
            'Visualization', 'need_printing', True,
            build_path_to_local_file('check_install.cfg')
        )

        self.config.config_vars = dict(
            DIST = get_config_var(
                self._config,
                'Installation', 'create_dist', True
            ),
            SETUP = get_config_var(
                self._config,
                'Installation', 'setup_project', True
            ),
            HOST = get_config_var(
                self._config,
                'Test server', 'HOST', '127.0.0.1'
            ),
            PORT = get_config_var(
                self._config,
                'Test server', 'PORT', 8000
            )
        )

    # Here is defioned commands wich used in code
    commands = dict(
        TEST = ("python",
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        "manage.py")
                ),
                "test",),
        CREATE_DIST = (
            "python",
            os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "../../setup.py")
            ),
            "sdist"
        ),
        SERVER = ("runserver", "{0}:{1}".format(
            config.config_vars['HOST'],
            config.config_vars['PORT'])),
        SYNCDB = ("syncdb",),
        INSTALL = (
            "python",
            os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "../../setup.py")
            ),
            "install",
        ),
    )
    '''
    ==============================
    Setup logging
    '''
    def _create_logger(self, name, file_name, level):
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

        if self.config.need_print:
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            log.addHandler(ch)
            log.debug("See info in logs {0} and {1}".format(
                self.config['error_log_path'],
                self.config['info_log_path'])
            )
        return log

    def create_loggers(self):
        f_name = __file__.split(".")[0]
        self.error_log = self._create_logger(
            f_name+"ERROR", self.config.error_log_path,
            logging.ERROR
        )
        self.info_log = self._create_logger(
            f_name+"INFO",
            self.config['info_log_path'],
            logging.INFO
        )


    def run_shell_cmd(self, cmd_args=[], info_msg="Command {0} was success.",
                      error_info="Command {0} failed.",
                      error_msg="Return code was {0}. Error was: {1}",
                      comm_msg="",
                      stdin=PIPE, stdout=PIPE, stderr=PIPE):
        '''
        This function runs commands in shell.
        '''
        #try:
        self.info_log.debug("Run command {0},",format(" ".join(cmd_args)))
        po = Popen(cmd_args, shell=False, stdin=stdin, stdout=stdout, stderr=stderr)
        #po.wait()
        out = po.stdout.read()
        error = po.stderr.read()
        self.info_log.info(out)
        self.error_log.error(error)
        out, error = po.communicate(comm_msg)

        self.info_log.info("Run command {0}.\n Result:\n {1}".format(" ".join(cmd_args), out))
        print "+"*100, "\n", " ".join(cmd_args)
        print "+"*100
        if po.returncode:
            self.info_log.debug(error_info.format(" ".join(cmd_args)))
            self.info_log.debug(error_msg.format(po.returncode, error))
            self.error_log.error(error_info.format(" ".join(cmd_args)))
            self.error_log.error(error_msg.format(po.returncode, error))
        else:
            self.info_log.info(info_msg.format(" ".join(cmd_args)))

        return po


    def install_service(self):
        exit_if_result(
            self.run_shell_cmd(
                self.commands['INSTALL'],
                error_info="Can not install service. Try to check permissions."
            )
        )

    #@trace_handler_error
    def handle(self, *args, **kwargs):
       # try to create dist
        if self.config.config_vars['DIST']:
            exit_if_result(
                self.run_shell_cmd(
                    self.commands['CREATE_DIST'],
                    error_info=("Cannot create dist. Command {0} failed."
                               "Please check setup.py file."),
                )
            )

        # try to install service
        if self.config.config_vars['SETUP']:
            self.install_service()

        time.sleep(3)
        print "Dealing with tests"
        #try:
            #import annotation_server
        #except ImportError:
            #error_log.error("You have no installed service correctly! Please reinstall it.")
            #info_log.debug("You have no installed service correctly! Please reinstall it.")
            #sys.exit(1)

        """
        ===============================
        Setup django settings module.
        """
        try:
            from django.core.management import setup_environ #, call_command
        except ImportError:
            self.error_log.error("Can not import django.")

        try:
            from annotation_server import settings
        except ImportError:
            self.error_log.error("Can not import project. Or try re-run current script.")

        db = {
            'default': {
                'ENGINE': 'sqlite3',
                'NAME': ':memory:'
            }
        }

        setattr(settings, 'DATABASES', db)

        setup_environ(settings)


        exit_if_result(
            self.run_shell_cmd(
                self.commands['TEST'],
                error_info="Tests failed. Check code or tests."
            )
        )


if __name__ == '__main__':
    CheckInstall()()
