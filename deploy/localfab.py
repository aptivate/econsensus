import os
from fabric.api import abort, env, require, settings, sudo
from fabric.contrib import files

# this is our common file that can be copied across projects
# we deliberately import all of this to get all the commands it
# provides as fabric commands
import fablib

# project_settings - try not to repeat ourselves so much ...
import project_settings

#
# These commands set up the environment variables
# to be used by later commands
#

def staging():
    """ use staging environment on remote host to demo to client"""
    env.project_dir = project_settings.project_name + '_test'
    env.environment = 'staging'
    env.hosts = ['lin-' + project_settings.project_name + '.aptivate.org:48001']
    fablib._setup_paths(project_settings)

def deploy(revision=None):
    """ update remote host environment (virtualenv, deploy, update) """
    require('project_root', provided_by=env.valid_envs)
    with settings(warn_only=True):
        fablib.apache_cmd('stop')
    if not files.exists(env.project_root):
        sudo('mkdir -p %(project_root)s' % env)
    fablib.checkout_or_update(revision)
    fablib.update_requirements()
    fablib.create_private_settings()
    fablib.link_local_settings()
    fablib.rm_pyc_files()
    fablib.update_db()
    if env.environment == 'production':
        fablib.setup_db_dumps()
    if env.environment.startswith('production'):
        fablib.link_apache_conf('production')
    else:
        fablib.link_apache_conf()
    fablib.load_fixtures()

    fablib.apache_cmd('start')

def load_fixtures():
    """load fixtures for this environment"""
    require('tasks_bin', provided_by=env.valid_envs)
    with settings(warn_only=True):
        sudo(env.tasks_bin + ' load_admin_user:' + env.environment)
        sudo(env.tasks_bin + ' load_django_site_data:' + env.environment)
        sudo(env.tasks_bin + ' load_sample_data:' + env.environment)

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
        abort('No apache conf file found - expected %s' % conf_file)
    if not files.exists(apache_conf):
        sudo('ln -s %s %s' % (conf_file, apache_conf))
    fablib.configtest()

def add_cron_email():
    require('tasks_bin', provided_by=env.valid_envs)
    with settings(warn_only=True):
        sudo(env.tasks_bin + ' add_cron_email:' + env.environment)

