from fabric.api import *
from fabric import utils
from fabric.decorators import hosts

# this is our common file that can be copied across projects
# we deliberately import all of this to get all the commands it
# provides as fabric commands
from fablib import *
import fablib
import project_settings

env.home = '/var/django/'
env.project = project_settings.project_name
# the top level directory on the server
env.project_dir = env.project

# repository type can be "svn" or "git"
env.repo_type = "git"
env.repository = 'git://github.com/aptivate/openconsent.git'

env.django_dir = os.path.join('django', env.project)
env.django_apps = ['publicweb', ]
env.test_cmd = ' manage.py test -v0 ' + ' '.join(env.django_apps)


# put "django" here if you want django specific stuff to run
# put "plain" here for a basic apache app
env.project_type = "django"

# does this virtualenv for python packages
env.use_virtualenv = True

# valid environments - used for require statements in fablib
env.valid_non_prod_envs = ('dev_server', 'staging_test', 'staging')
env.valid_envs = ('dev_server', 'staging_test', 'staging', 'production')

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

def dev_server():
    """ use dev environment on remote host to play with code in production-like env"""
    utils.abort('remove this line when dev server setup')
    env.environment = 'dev_server'
    env.hosts = ['fen-vz-' + project_settings.project_name + '-dev']
    _local_setup()


def staging_test():
    """ use staging environment on remote host to run tests"""
    # this is on the same server as the customer facing stage site
    # so we need project_root to be different ...
    env.project_dir = env.project + '_test'
    env.environment = 'staging_test'
    env.use_apache = False
    env.hosts = ['fen-vz-' + project_settings.project_name]
    _local_setup()


def staging():
    """ use staging environment on remote host to demo to client"""
    env.environment = 'staging'
    env.hosts = ['fen-vz-' + project_settings.project_name]
    _local_setup()


def production_sandbox():
    """ use staging environment on remote host to run tests"""
    # this is on the same server as the customer facing stage site
    # so we need project_root to be different ...
    env.project_dir = env.project + '_sandbox'
    env.environment = 'production_sandbox'
    env.hosts = ['lin-' + project_settings.project_name + '.aptivate.org:48001']
    _local_setup()


def production():
    """ use production environment on remote host"""
    env.environment = 'production'
    env.hosts = ['lin-' + project_settings.project_name + '.aptivate.org:48001']
    _local_setup()
    
def production_houseofawesome():
    """ use production environment on remote host"""
    env.project_dir = env.project + '_houseofawesome'
    env.environment = 'production_houseofawesome'
    env.hosts = ['lin-' + project_settings.project_name + '.aptivate.org:48001']
    _local_setup()

def production_seedltd():
    """ use production environment on remote host"""
    env.project_dir = env.project + '_seedltd'
    env.environment = 'production_seedltd'
    env.hosts = ['lin-' + project_settings.project_name + '.aptivate.org:48001']
    _local_setup()

def deploy(revision=None):
    """ update remote host environment (virtualenv, deploy, update) """
    require('project_root', provided_by=env.valid_envs)
    with settings(warn_only=True):
        apache_cmd('stop')
    if not files.exists(env.project_root):
        sudo('mkdir -p %(project_root)s' % env)
    checkout_or_update(revision)
    update_requirements()
    create_private_settings()
    link_local_settings()
    rm_pyc_files()
    update_db()
    if env.environment == 'production':
        setup_db_dumps()
    if env.environment.startswith('production'):
        link_apache_conf('production')
    else:
        link_apache_conf()
    load_fixtures()
    
    apache_cmd('start')
    
def load_fixtures():
    """load fixtures for this environment"""
    require('tasks_bin', provided_by=env.valid_envs)
    with settings(warn_only=True):
        sudo(env.tasks_bin + ' load_admin_user:' + env.environment)
        sudo(env.tasks_bin + ' load_django_site_data:' + env.environment)

def load_sample_data():
    """load fixtures for this environment"""
    require('tasks_bin', provided_by=env.valid_envs)
    sudo(env.tasks_bin + ' load_sample_data')

def link_apache_conf(apache_conf_name=None):
    """link the apache.conf file"""
    require('vcs_root', provided_by=env.valid_envs)
    if apache_conf_name == None:
        apache_conf = os.path.join('/etc/httpd/conf.d', env.project+'_'+env.environment+'.conf')
        conf_file = os.path.join(env.vcs_root, 'apache', env.environment+'.conf')
    else:
        # this assumes that each server will only have one DNS name, ie there is
        # only one VirtualHost directive per server. If this changes you might
        # want to go back to the fablib version of this function
        # So we only ever have one file in /etc/httpd/conf.d that links to the
        # apache conf in the last deployed instance
        apache_conf = os.path.join('/etc/httpd/conf.d', env.project+'.conf')
        conf_file = os.path.join(env.vcs_root, 'apache', apache_conf_name+'.conf')
        if files.exists(apache_conf):
            sudo('rm %s' % apache_conf)
    if not files.exists(conf_file):
        utils.abort('No apache conf file found - expected %s' % conf_file)
    if not files.exists(apache_conf):
        sudo('ln -s %s %s' % (conf_file, apache_conf))
    configtest()
