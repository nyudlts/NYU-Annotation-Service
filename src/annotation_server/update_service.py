#! /usr/bin/python
'''
File: update_service.py
Author: Alex Boiko
Description: This script updates already installed service on the current machine.
    Remove the source codes, then check out the project and install it.
'''

from subprocess import Popen, PIPE
import os
import sys
from check_installation import CheckInstall
from pip import main as pip_run_command
from mercurial import hg, commands, ui
from django.core.management import call_command, setup_environ, color

from optparse import make_option, OptionParser
from helpers import BaseCommand
from helpers import trace_handler_error

CONFIG_FILE_PATH = 'update_service.cfg'


class UpdateError(Exception):
    pass

class Updater(BaseCommand):
    """This class will update the source codes of the project"""

    option_list = BaseCommand.option_list + (
        make_option('-p', '--repo_path', action='store', dest='repo_path', default='',
                    type='string',
                    help='Where repository is located (path).'),
        make_option('--with-logs', action='store_false', dest='with_logs', default=False,
                    help='Need logging?')
    )

    def check_repo_type(self):
        repos = {
            '.svn': 'svn',
            '.git': 'git',
            '.hg': 'hg',
        }
        for path, dirs, files in os.walk(self.repo_path):
            exist_repos = [r for r in repos if r in dirs]
            if len(exist_repos) > 1:
                raise Exception("Select only one repository type")
            return repos[exist_repos[0]]

    def checkout(self):
        repo_type = self.check_repo_type()
        checker = getattr(self, 'checkout_'+repo_type, None)
        if not checker:
            raise Exception("Checkout function for {0} repository type"
                            "does not exists".format(repo_type))
        commands = checker()
        if isinstance(commands, (list, tuple)):
            p = Popen(commands, shell=False,
                      stdin=PIPE, stdout=PIPE, stderr=PIPE)
            out = p.stdout.read()
            err = p.stderr.read()
            if err:
                print "\n\n Error: \n"
                print "\t {}".format(err)
            print "Command out was: \n\t".format(out)



    #@trace_handler_error
    def handle(self, *args, **kwargs):
        self.repo_path = os.path.abspath(
            kwargs.get('repo_path') or os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        '..', '..',
                    )
                )
            )

        print self.repo_path
        # First of all we need to check installed or not the server.
        self._installed = self._is_installed()
        if self._installed:
            print "\n\nProject already installed."
            # remove sources
            self.remove_proj()
            # checkout new version
            self.checkout()
            # install service again
            CheckInstall().install_service()
            # here need to implement working with migrations
            self.migrate_project()
        else:
            print "\n\nProject NOT installed."
        #elif os.path.exists(os.path.realpath(os.path.join(self.repo_path, '.hg'))):
            # in this case we think that service is not installed
            # or installed in the same dir
            self.checkout()
            CheckInstall().install_service()
            self.migrate_project()
        #else:

            #raise UpdateError("\nService not installed. Install it, then try to update!\n")

    def _run_pip(self, cmd):
        sys.argv = ['pip'] + list(cmd)
        return pip_run_command(cmd)

    def _is_installed(self):
        try:
            import annotation_server
            self.path = annotation_server.__file__
            return True
        except ImportError:
            return False

    def remove_proj(self):
        # if service is already installed we have to try $pip uninstall
        self._run_pip(["uninstall", "annotation_server", '--yes'])
        return

    def checkout_hg(self):
        return 'hg', 'st'
        # pull new version of project from perository
        if not self.repo_path:
            # may be need to find repo recursively from this dir to up, but it's only may be.
            self.repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',))
        repo = hg.repository(
            ui.ui(),
            self.repo_path
        )
        url = dict(repo.ui.configitems('paths', 'default'))['default']
        commands.pull(ui.ui(), repo, url)
        # and update it
        commands.update(ui.ui(), repo)
        return

    def checkout_svn(self):
        return 'svn', 'up'


    def checkout_git(self):
        return 'git', 'up'

    def migrate_project(self):
        if self._is_installed:
            from annotation_server import settings
            setup_environ(settings)
            #from django.conf import settings
            if 'south' in settings.INSTALLED_APPS:
                call_command('migrate', noinput=True)
                # run migrations
            return True


if __name__ == '__main__':
    u = Updater()()
