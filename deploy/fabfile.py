import os
import sys
import errno

from fabric.api import env
#from fabric.api import *
from fabric import utils

# deliberately import * - so fabric will treat it as a name
from fablib import *
# this is so we can call commands not imported by the above, basically
# commands that start with an underscore
import fablib

# Per project tasks can be defined in a file called localfab.py - we will
# import the functions from localfab.py if it exists. But first we need to
# know where to look.

# This fabfile can be called normally (in the same directory) or it can be
# installed as a python package, in which case the fab.py wrapper can call
# it from the directory that contains project_settings.py (and, optionally,
# localfab.py) It communicates which directory that is through an environment
# variable.
if 'PROJECTDIR' in os.environ:
    # add the project directory to the python path, if set in environ
    sys.path.append(os.environ['PROJECTDIR'])
    localfabdir = os.environ['PROJECTDIR']
else:
    localfabdir = os.path.dirname(__file__)

# import the project settings
import project_settings


#
# These commands set up the environment variables
# to be used by later commands
#
def _server_setup(environment):
    if environment not in project_settings.host_list:
        utils.abort('%s not defined in project_settings.host_list' % environment)
    env.environment = environment
    env.hosts = project_settings.host_list[environment]
    fablib._setup_paths(project_settings)


def dev():
    """
    Test fabric scripts locally
    Setup steps ...
    1) To allow fabric to ssh to localhost:
        sudo apt-get install openssh-server
    2) To avoid failure at correct_log_perms as probably no apache user on localhost
        sudo adduser apache
    3) ROOT_DIR below points to an absolute path for fabric deployment to act within
    4) Override env.repository below if necessary
    """
    ROOT_DIR = '/tmp/fabtesting/'
    #ROOT_DIR = '/home/joanna/Code/aptivate/fabtesting/'
    try:
        os.makedirs(ROOT_DIR)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(ROOT_DIR):
            pass
        else:
            raise
    env.environment = 'dev'
    env.hosts = ['localhost']
    env.home = os.path.join(ROOT_DIR, env.home.strip('/'))
    env.use_apache = False
    env.branch = 'develop'
    _local_setup()


def dev_server():
    """ use dev environment on remote host to play with code in production-like env"""
    _server_setup('dev_server')


def staging_test():
    """ use staging environment on remote host to run tests"""
    # this is on the same server as the customer facing stage site
    # so we need project_root to be different ...
    env.project_dir = env.project_name + '_test'
    env.webserver = None
    _server_setup('staging_test')


def staging():
    """ use staging environment on remote host to demo to client"""
    _server_setup('staging')


def production():
    """ use production environment on remote host"""
    _server_setup('production')

# now see if we can find localfab
# it is important to do this after importing from fablib, and after
# defining the above functions, so that functions in localfab can
# override those in fablib and fabfile.
#
# We deliberately don't surround the import by try/except. If there
# is an error in localfab, you want it to blow up immediately, rather
# than silently fail.
localfab = None
if os.path.isfile(os.path.join(localfabdir, 'localfab.py')):
    from localfab import *
