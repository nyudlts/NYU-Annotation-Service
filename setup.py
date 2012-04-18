#! python

'''
This file will setup Annotations service on you computer.
'''
from setuptools import setup, find_packages
import os
import sys
import re

#raise Exception()

root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)


def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'(\s*git)|(\s*hg)', line):
            pass
        else:
            requirements.append(line)
    return requirements


def parse_dependency_links(file_name, install_flag=False):
    dependency_links = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'\s*-e\s+', line):
            dependency_links.append(re.sub(r'\s*-e\s+', '', line))
        if re.match(r'(\s*git)|(\s*hg)', line):
            if install_flag == True:
                line_arr = line.split('/')
                line_arr_length = len(line.split('/'))
                pck_name = line_arr[line_arr_length - 1].split('.git')
                if len(pck_name) == 2:
                    os.system('pip install -f %s %s' % (pck_name[0], line))
                if len(pck_name) == 1:
                    os.system('pip install -f %s %s' % (pck_name, line))
    return dependency_links


# taken from django-registration
# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []

for dirpath, dirnames, filenames in os.walk('src/annotation_server'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        for f in filenames:
            data_files.append(os.path.join(dirpath, f))


install_flag=False
if len(sys.argv) >= 2 and sys.argv[1] == "install":
    install_flag = True


help_file = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        'README.txt')
)

setup(
    name='annotation_server',
    version="0.1a",
    description=help_file,
    author='Alex Boiko',
    author_email='aboiko@exadel.com',
    url='https://bitbucket.org/alex_bojko/nyu',

    include_package_data=True,

    #zip_safe = False,
    #packages=[
        #'src/annotation_server',
        #'src/annotation_server/api'
    #],

    packages=find_packages('src', exclude=('local_settings',)),
    package_dir={
        '': 'src'
    },

    exclude_package_data={'': ['local_settings']},
    #package_data={'':data_files},
    #{
        #'': ["src/annotation_server/media/*"],
        #'': ["src/annotation_server/templates/*"],
        #'': ['src/annotation_server/annotation_service.sh',]
    #}, #data_files},

    scripts=(
        'src/annotation_server/annotation_service.sh',
        'src/annotation_server/update_service.py',
        'src/annotation_server/check_installation.py',
    ),

    install_requires = parse_requirements('./pip_req.txt'),
    dependency_links = parse_dependency_links('./pip_req.txt',
                                              install_flag),
    classifiers=[
    ],
    platforms=["win", "linux"],

)

