import os
from os import path
from datetime import datetime
from fabric.api import env, require, settings, sudo

# this is our common file that can be copied across projects
# we deliberately import all of this to get all the commands it
# provides as fabric commands
import fablib


def deploy(revision=None, keep=None):
    """ update remote host environment (virtualenv, deploy, update) """
    require('server_project_home', provided_by=env.valid_envs)
    fablib._migrate_directory_structure()
    fablib._set_vcs_root_dir_timestamp()
    fablib._create_dir_if_not_exists(env.server_project_home)

    fablib.check_for_local_changes(revision)

    fablib.create_copy_for_next()
    fablib.checkout_or_update(in_next=True, revision=revision)
    fablib.rm_pyc_files(path.join(env.next_dir, env.relative_django_dir))
    # create the deploy virtualenv if we use it
    fablib.create_deploy_virtualenv(in_next=True)

    # we only have to disable this site after creating the rollback copy
    # (do this so that apache carries on serving other sites on this server
    # and the maintenance page for this vhost)
    downtime_start = datetime.now()
    fablib.link_webserver_conf(maintenance=True)
    with settings(warn_only=True):
        fablib.webserver_cmd('reload')
    fablib.point_current_to_next()

    # Use tasks.py deploy:env to actually do the deployment, including
    # creating the virtualenv if it thinks it necessary, ignoring
    # env.use_virtualenv as tasks.py knows nothing about it.
    fablib._tasks('deploy:' + env.environment)

    # bring this vhost back in, reload the webserver and touch the WSGI
    # handler (which reloads the wsgi app)
    fablib.link_webserver_conf()
    fablib.webserver_cmd('reload')
    downtime_end = datetime.now()
    fablib.touch_wsgi()

    correct_log_perms()

    fablib.delete_old_rollback_versions(keep)
    if env.environment == 'production':
        fablib.setup_db_dumps()

    fablib._report_downtime(downtime_start, downtime_end)


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
