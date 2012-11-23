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

def deploy(revision=None):
    """ update remote host environment (virtualenv, deploy, update) """
    require('project_root', provided_by=env.valid_envs)
    with settings(warn_only=True):
        fablib.webserver_cmd('stop')
    if not files.exists(env.project_root):
        sudo('mkdir -p %(project_root)s' % env)
    fablib.checkout_or_update(revision)
    fablib._tasks('deploy:' + env.environment)
    fablib.rm_pyc_files()
    fablib.collect_static_files()
    fablib.update_db()
    if env.environment == 'production':
        fablib.setup_db_dumps()
    if env.environment.startswith('production'):
        link_webserver_conf('production')
    else:
        link_webserver_conf()
    load_fixtures()
    correct_log_perms()

    fablib.webserver_cmd('start')

def load_fixtures():
    """load fixtures for this environment"""
    require('tasks_bin', provided_by=env.valid_envs)
    with settings(warn_only=True):
        sudo(env.tasks_bin + ' load_admin_user:' + env.environment)
        sudo(env.tasks_bin + ' load_django_site_data:' + env.environment)
        sudo(env.tasks_bin + ' load_sample_data:' + env.environment)

def link_webserver_conf(webserver_conf_name=None):
    """link the webserver.conf file"""
    require('vcs_root', provided_by=env.valid_envs)
    if webserver_conf_name == None:
        webserver_conf = os.path.join('/etc/httpd/conf.d', env.project_name+'_'+env.environment+'.conf')
        conf_file = os.path.join(env.vcs_root, env.webserver, env.environment+'.conf')
    else:
        # this assumes that each server will only have one DNS name, ie there is
        # only one VirtualHost directive per server. If this changes you might
        # want to go back to the fablib version of this function
        # So we only ever have one file in /etc/httpd/conf.d that links to the
        # webserver conf in the last deployed instance
        webserver_conf = os.path.join('/etc/httpd/conf.d', env.project+'.conf')
        conf_file = os.path.join(env.vcs_root, 'webserver', webserver_conf_name+'.conf')
        if files.exists(webserver_conf):
            sudo('rm %s' % webserver_conf)
    if not files.exists(conf_file):
        abort('No webserver conf file found - expected %s' % conf_file)
    if not files.exists(webserver_conf):
        sudo('ln -s %s %s' % (conf_file, webserver_conf))
    fablib.webserver_configtest()

def add_cron_email():
    require('tasks_bin', provided_by=env.valid_envs)
    with settings(warn_only=True):
        sudo(env.tasks_bin + ' add_cron_email:' + env.environment)

def correct_log_perms():
    require('project_root', provided_by=env.valid_envs)
    sudo('chown apache /var/log/httpd')
    sudo('touch /var/log/httpd/econsensus.log')
    sudo('chown apache /var/log/httpd/econsensus.log')
