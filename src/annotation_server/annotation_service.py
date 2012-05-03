#!/usr/bin/python

from helpers import BaseCommand
from optparse import make_option, OptionParser


from django.core.management import call_command, setup_environ
import multiprocessing
from subprocess import Popen
import os, sys, pdb

try:
    # non local import
    from annotation_server import settings
except ImportError as e:
    # try to do local import
    try:
        import settings
    except ImportError as e:
        raise Exception("Settings file does not exists! Where is it?")

PID = getattr(settings, "PID", None)
SOCKET = getattr(settings, "SOCKET", None)

if not (PID and SOCKET):
    PID = "/www/sites/annotations/log/django.pid"
    SOCKET = "/www/sites/annotations/log/django.sock"


class ArgvHandler(object):
    '''
    This class routes first argument from command line to
    method with the same name.
    If there's more than one args they will passed to the handler function as args.

    '''
    def __init__(self):
        if len(sys.argv) > 1:
            self.command_name = sys.argv[1].replace(' ', '_')
            self.args = [
                i for i in sys.argv[2:]
            ]
       # setup django env
        else:
            self.command_name = "_help"
            self.args = []
        setup_environ(settings)

    def __call__(self):
        command = getattr(self, self.command_name, None)
        if not callable(command):
            raise NotImplementedError("This command doesn't recognized!")
        command(*self.args)

    def _help(self):
        print "Here is all commands which you can run:"
        print "\n".join([" - " + i for i in self.__class__.__dict__.keys() if not i.startswith('_') ])

    def _run_command(self, cmd):
        if len(cmd) < 2:
            cmd += dict()
        return call_command(cmd[0], **cmd[1])

    def start(self, *a, **k):
        print "Statring annotation service"
        print ''
        print "PID file is located in {}".format(PID)
        print "Socket file is located in {}".format(SOCKET)
        print ''
        cmd = ("runfcgi", "socket={0}".format(SOCKET),
               "maxchildren=10",
               "maxspare=5",
               "minspare=2",
               "method=prefork",
               "pidfile={0}".format(PID),
               "daemonize=True"
              )
        call_command(*cmd)

    def syncdb(self, *a, **k):
        call_command("syncdb")
        call_command("migrate", *a)

    def start_dev(self, *a, **k):
        call_command('runserver', *a, **k)

    def stop(self, *a, **k):
        try:
            pid = int(open(PID,'r').read())
            os.kill(pid, 9)
            os.remove(PID)
            print "Stopping server..."
        except (ValueError, IOError) as e:
            print "Service is not runned!"
            print e

    def restart(self, *a, **k):
        self.stop()
        self.start()



if __name__ == '__main__':
    #if 'pdb' in sys.argv:
    #pdb.set_trace()
    ArgvHandler()()

