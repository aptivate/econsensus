from fabric.api import env, require, settings, sudo
from fabric.contrib import files

# this is our common file that can be copied across projects
# we deliberately import all of this to get all the commands it
# provides as fabric commands
import fablib

def deploy(revision=None):
    """ update remote host environment (virtualenv, deploy, update) """
    require('project_root', provided_by=env.valid_envs)
    fablib.link_webserver_conf(unlink=True)
    with settings(warn_only=True):
        fablib.webserver_cmd('reload')
    if not files.exists(env.project_root):
        sudo('mkdir -p %(project_root)s' % env)
    fablib.checkout_or_update(revision)
    # Use tasks.py deploy:env to actually do the deployment, including
    # creating the virtualenv if it thinks it necessary, ignoring
    # env.use_virtualenv as tasks.py knows nothing about it.
    fablib._tasks('deploy:' + env.environment)
    fablib.rm_pyc_files()
    fablib.collect_static_files()
    fablib.update_db()
    if env.environment == 'production':
        fablib.setup_db_dumps()
    load_fixtures()
    correct_log_perms()

    fablib.link_webserver_conf()
    fablib.webserver_cmd('reload')

def load_fixtures():
    """load fixtures for this environment"""
    require('tasks_bin', provided_by=env.valid_envs)
    with settings(warn_only=True):
        sudo(env.tasks_bin + ' load_admin_user:' + env.environment)
        sudo(env.tasks_bin + ' load_django_site_data:' + env.environment)
        sudo(env.tasks_bin + ' load_sample_data:' + env.environment)

def add_cron_email():
    require('tasks_bin', provided_by=env.valid_envs)
    with settings(warn_only=True):
        sudo(env.tasks_bin + ' add_cron_email:' + env.environment)

def correct_log_perms():
    require('project_root', provided_by=env.valid_envs)
    sudo('chown apache /var/log/httpd')
    sudo('touch /var/log/httpd/econsensus.log')
    sudo('chown apache /var/log/httpd/econsensus.log')
