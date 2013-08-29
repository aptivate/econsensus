import os
from fabric.api import env, require, settings, sudo
from fabric.contrib import files

# this is our common file that can be copied across projects
# we deliberately import all of this to get all the commands it
# provides as fabric commands
import fablib


def deploy(revision=None, keep=None):
    """ update remote host environment (virtualenv, deploy, update) """
    require('vcs_root_dir', provided_by=env.valid_envs)
    fablib.check_for_local_changes()
    fablib.link_webserver_conf(unlink=True)
    with settings(warn_only=True):
        fablib.webserver_cmd('reload')
    if not files.exists(env.vcs_root_dir):
        sudo('mkdir -p %(vcs_root_dir)s' % env)
    if files.exists(env.vcs_root_dir):
        fablib.create_copy_for_rollback(keep)
    fablib.checkout_or_update(revision)
    fablib.create_deploy_virtualenv()
    # Use tasks.py deploy:env to actually do the deployment, including
    # creating the virtualenv if it thinks it necessary, ignoring
    # env.use_virtualenv as tasks.py knows nothing about it.
    fablib._tasks('deploy:' + env.environment)
    fablib.rm_pyc_files()
    if env.environment == 'production':
        fablib.setup_db_dumps()
    correct_log_perms()

    fablib.link_webserver_conf()
    fablib.webserver_cmd('reload')
    fablib.touch_wsgi()


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
    require('django_dir', provided_by=env.valid_envs)
    log_path = os.path.join(env.django_dir, 'log', 'econsensus.log')
    sudo('touch %s' % log_path)
    sudo('chown apache %s' % log_path)
    sudo('chown apache /var/log/httpd')
    sudo('touch /var/log/httpd/econsensus.log')
    sudo('chown apache /var/log/httpd/econsensus.log')
