#!/usr/bin/python

from annotation_server.helpers import BaseCommand
from optparse import make_option, OptionParser


from django.core.management import call_command, setup_environ
import multiprocessing
from subprocess import Popen
from annotation_server import settings
import os, sys, pdb


PID = "/www/sites/annotations/log/django.pid"
SOCKET = "/www/sites/annotations/log/django.sock"

PID = "/tmp/annotation.pid"
SOCKET = "/tmp/annotation.socket"


class ArgvHandler(object):
    '''
    This class routes first argument from command line to
    method with the same name.
    If there's more than one args they will passed to the handler function as args.

    '''
    def __init__(self):
        self.command_name = sys.argv[1].replace(' ', '_')
        self.args = [
            i for i in sys.argv[2:]
        ]
        # setup django env
        setup_environ(settings)


    def __call__(self):
        command = getattr(self, self.command_name, None)
        if not callable(command):
            raise NotImplementedError("This command doesn't recognized!")
        command(*self.args)

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

