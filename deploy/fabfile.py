import errno

from fabric.api import *
from fabric import utils
from fabric.decorators import hosts

# this is our common file that can be copied across projects
# we deliberately import all of this to get all the commands it
# provides as fabric commands
from fablib import *
import fablib

# project_settings - try not to repeat ourselves so much ...
import project_settings

env.home = '/var/django/'
env.project = project_settings.project_name
# the top level directory on the server
env.project_dir = env.project

# repository type can be "svn" or "git"
env.repo_type = "git"
env.repository = 'git://github.com/aptivate/econsensus.git'

env.django_dir = os.path.join('django', env.project)
env.test_cmd = ' manage.py test -v0 ' + ' '.join(project_settings.django_apps)

env.project_type = project_settings.project_type

# does this virtualenv for python packages
env.use_virtualenv = True

# valid environments - used for require statements in fablib
env.valid_non_prod_envs = ('dev', 'dev_server', 'staging_test', 'staging')
env.valid_envs = ('dev', 'dev_server', 'staging_test', 'staging', 'production')

# does this use apache - mostly for staging_test
env.use_apache = True


# this function can just call the fablib _setup_path function
# or you can use it to override the defaults
def _local_setup():
    # put your own defaults here
    fablib._setup_path()
    # override settings here
    # if you have an ssh key and particular user you need to use
    # then uncomment the next 2 lines
    #env.user = "root" 
    #env.key_filename = ["/home/shared/keypair.rsa"]


#
# These commands set up the environment variables
# to be used by later commands
#


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
    ROOT_DIR = '/tmp/fabtesting/'#'/home/joanna/Code/aptivate/fabtesting/'
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
    utils.abort('remove this line when dev server setup')
    env.environment = 'dev_server'
    env.hosts = ['fen-vz-' + project_settings.project_name + '-dev' + '.fen.aptivate.org']
    _local_setup()


def staging_test():
    """ use staging environment on remote host to run tests"""
    # this is on the same server as the customer facing stage site
    # so we need project_root to be different ...
    env.project_dir = env.project + '_test'
    env.environment = 'staging_test'
    env.use_apache = False
    env.hosts = ['fen-vz-' + project_settings.project_name + '.fen.aptivate.org']
    _local_setup()


def staging():
    """ use staging environment on remote host to demo to client"""
    env.environment = 'staging'
    env.hosts = ['fen-vz-' + project_settings.project_name + '.fen.aptivate.org']
    _local_setup()


def production():
    """ use production environment on remote host"""
    env.environment = 'production'
    env.hosts = ['lin-' + project_settings.project_name + '.aptivate.org:48001']
    _local_setup()

def deploy(revision=None):
    """ update remote host environment (virtualenv, deploy, update) """
    require('project_root', provided_by=env.valid_envs)
    check_for_local_changes()

    fablib._create_dir_if_not_exists(env.project_root)
    if files.exists(env.vcs_root):
        create_copy_for_rollback(keep=1)
    link_apache_conf(unlink=True)
    with settings(warn_only=True):
        apache_cmd('reload')
    checkout_or_update(revision)
    # Use tasks.py deploy:env to actually do the deployment, including
    # creating the virtualenv if it thinks it necessary, ignoring
    # env.use_virtualenv as tasks.py knows nothing about it.
    fablib._tasks('deploy:' + env.environment)
    rm_pyc_files()
    if env.environment == 'production':
        setup_db_dumps()
    link_apache_conf()
    correct_log_perms()

    apache_cmd('reload')

def load_sample_data():
    """load sample data for this environment"""
    require('tasks_bin', provided_by=env.valid_envs)
    with settings(warn_only=True):
        sudo(env.tasks_bin + ' load_sample_data:' + env.environment)

def add_cron_email():
    require('tasks_bin', provided_by=env.valid_envs)
    with settings(warn_only=True):
        sudo(env.tasks_bin + ' add_cron_email:' + env.environment)

def correct_log_perms():
    require('project_root', provided_by=env.valid_envs)
    log_path = os.path.join(env.django_root, 'log', 'econsensus.log')
    sudo('chown apache %s' % log_path)

