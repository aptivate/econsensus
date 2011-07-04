import os, sys
import getpass
import time

from fabric.api import *
from fabric.contrib import files, console
from fabric.contrib.files import exists
from fabric import utils

def _setup_path():
    # TODO: something like
    # if not defined env.project_subdir:
    #     env.project_subdir = env.project
    # env.project_root    = os.path.join(env.home, env.project_subdir)

    # allow for the fabfile having set up some of these differently
    if not env.has_key('project_root'):
        env.project_root    = os.path.join(env.home, env.project_dir)
    if not env.has_key('vcs_root'):
        env.vcs_root        = os.path.join(env.project_root, 'dev')
    if not env.has_key('prev_root'):
        env.prev_root        = os.path.join(env.project_root, 'previous')
    if not env.has_key('dump_dir'):
        env.dump_dir        = os.path.join(env.project_root, 'dbdumps')
    if not env.has_key('deploy_root'):
        env.deploy_root     = os.path.join(env.vcs_root, 'deploy')
    env.tasks_bin = os.path.join(env.deploy_root, 'tasks.py')
    if env.project_type == "django" and not env.has_key('django_dir'):
        env.django_dir      = env.project
    if env.project_type == "django" and not env.has_key('django_root'):
        env.django_root     = os.path.join(env.vcs_root, env.django_dir)
    if env.use_virtualenv:
        if not env.has_key('virtualenv_root'):
            env.virtualenv_root = os.path.join(env.django_root, '.ve')
        if not env.has_key('python_bin'):
            env.python_bin      = os.path.join(env.virtualenv_root, 'bin', 'python2.6')
    if not env.has_key('settings'):
        env.settings        = '%(project)s.settings' % env


def _get_svn_user_and_pass():
    if not env.has_key('svnuser') or len(env.svnuser) == 0:
        # prompt user for username
        prompt('Enter SVN username:', 'svnuser')
    if not env.has_key('svnpass') or len(env.svnpass) == 0:
        # prompt user for password
        env.svnpass = getpass.getpass('Enter SVN password:')



def deploy_clean(revision=None):
    """ delete the entire install and do a clean install """
    if env.environment == 'production':
        utils.abort('do not delete the production environment!!!')
    require('project_root', provided_by=env.valid_non_prod_envs)
    # TODO: dump before cleaning database?
    with settings(warn_only=True):
        apache_cmd('stop')
    clean_db()
    sudo('rm -rf %s' % env.project_root)
    deploy(revision)


def deploy(revision=None):
    """ update remote host environment (virtualenv, deploy, update) """
    require('project_root', provided_by=env.valid_envs)
    with settings(warn_only=True):
        apache_cmd('stop')
    if files.exists(env.project_root):
        create_copy_for_rollback()
    else:
        sudo('mkdir -p %(project_root)s' % env)
    checkout_or_update(revision)
    if env.use_virtualenv:
        update_requirements()
    if env.project_type == "django":
        link_local_settings()
        rm_pyc_files()
        update_db()
        if env.environment == 'production':
            setup_db_dumps()
    link_apache_conf()
    apache_cmd('start')


def create_copy_for_rollback():
    """Copy the current version out of the way so we can rollback to it if required."""
    require('prev_root', 'vcs_root', 'tasks_bin', provided_by=env.valid_envs)
    # create directory for it
    prev_dir = os.path.join(env.prev_root, time.strftime("%Y-%m-%d_%H-%M-%S"))
    sudo('mkdir -p %s' % prev_dir)
    # cp -a
    sudo('cp -a %s %s' % (env.vcs_root, prev_dir))
    # dump database
    with cd(prev_dir):
        sudo(env.tasks_bin + ' dump_db')


def rollback(version='last', migrate=False, restore_db=False):
    """Redeploy one of the old versions.

    Arguments are 'version', 'migrate' and 'restore_db':

    * if version is 'last' (the default) then the most recent version will be
      restored. Otherwise specify by timestamp - use list_previous to get a list
      of available versions.
    * if restore_db is True, then the database will be restored as well as the
      code. The default is False.
    * if migrate is True, then fabric will attempt to work out the new and old
      migration status and run the migrations to match the database versions. 
      The default is False

    Note that migrate and restore_db cannot both be True."""
    utils.abort('rollback has not been implemented yet')
    if migrate and restore_db:
        utils.abort('rollback cannot do both migrate and restore_db')
    if migrate:
        utils.abort("rollback: haven't worked out how to do migrate yet ...")

    if version == 'last':
        # get the latest directory from prev_dir
        pass
        # list directories in env.prev_root, use last one
    else:
        # check version specified exists
        rollback_dir = os.path.join(env.prev_root, version)
        if not files.exists(rollback_dir):
            utils.abort("Cannot rollback to version %s, it does not exist, use list_previous to see versions available" % version)
        
    # first copy this version out of the way
    create_copy_for_rollback()
    # delete everything - don't want stray files left over
    # cp -a from rollback_dir to vcs_root
    if restore_db:
        # feed the dump file into mysql command
        pass


def list_previous():
    """List the previous versions available to rollback to."""
    utils.abort('list_previous has not been implemented yet')
    # list the previous directory, convert to format.
    # could also determine the VCS revision number


def delete_old_versions(keep=5):
    """Delete old rollback directories, keeping the last "keep" (default 5)"."""
    utils.abort('delete_old_versions has not been implemented yet')


def local_test():
    """ run the django tests on the local machine """
    require('project')
    with cd(os.path.join("..", env.project)):
        local("python " + env.test_cmd, capture=False)


def remote_test():
    """ run the django tests remotely - staging only """
    require('django_root', 'python_bin', 'test_cmd', provided_by=env.valid_non_prod_envs)
    with cd(env.django_root):
        sudo(env.python_bin + env.test_cmd)


def checkout_or_update(revision=None):
    """ checkout or update the project from version control.
    
    This command works with both svn and git repositories.
    
    You can also specify a revision to checkout, as an argument."""
    require('project_root', 'repo_type', 'vcs_root', 'repository',
        provided_by=env.valid_envs)
    if env.repo_type == "svn":
        # function to ask for svnuser and svnpass
        _get_svn_user_and_pass()
        # if the .svn directory exists, do an update, otherwise do
        # a checkout
        if files.exists(os.path.join(env.vcs_root, ".svn")):
            cmd = 'svn update --non-interactive --username %s --password %s' % (env.svnuser, env.svnpass)
            if revision:
                cmd += " --revision " + revision
            with cd(env.vcs_root):
                with hide('running'):
                    sudo(cmd)
        else:
            cmd = 'svn checkout --non-interactive --username %s --password %s %s' % (env.svnuser, env.svnpass, env.repository)
            if revision:
                cmd += "@" + revision
            with cd(env.project_root):
                with hide('running'):
                    sudo(cmd)
    elif env.repo_type == "git":
        # if the .git directory exists, do an update, otherwise do
        # a clone
        if files.exists(os.path.join(env.vcs_root, ".git")):
            with cd(env.vcs_root):
                sudo('git pull')
        else:
            with cd(env.project_root):
                sudo('git clone %s dev' % env.repository)
        if revision:
            with cd(env.project_root):
                sudo('git checkout %s' % revision)


def update_requirements():
    """ update external dependencies on remote host """
    require('tasks_bin', provided_by=env.valid_envs)
    sudo(env.tasks_bin + ' update_ve')


def clean_db(revision=None):
    """ delete the entire database """
    if env.environment == 'production':
        utils.abort('do not delete the production database!!!')
    require('tasks_bin', provided_by=env.valid_non_prod_envs)
    sudo(env.tasks_bin + " clean_db")

def update_db():
    """ create and/or update the database, do migrations etc """
    require('tasks_bin', provided_by=env.valid_envs)
    sudo(env.tasks_bin + ' update_db')

def setup_db_dumps():
    """ set up mysql database dumps """
    require('dump_dir', provided_by=env.valid_envs)
    sudo(env.tasks_bin + ' setup_db_dumps:' + env.dump_dir)

def touch():
    """ touch wsgi file to trigger reload """
    require('vcs_root', provided_by=env.valid_envs)
    wsgi_dir = os.path.join(env.vcs_root, 'wsgi')
    sudo('touch ' + os.path.join(wsgi_dir, 'wsgi_handler.py'))


def link_local_settings():
    """link the local_settings.py file for this environment"""
    require('tasks_bin', provided_by=env.valid_envs)
    sudo(env.tasks_bin + ' link_local_settings:' + env.environment)

    # check that settings imports local_settings, as it always should,
    # and if we forget to add that to our project, it could cause mysterious
    # failures
    run('grep -q "^from local_settings import \*" %s' %
        os.path.join(env.django_root, 'settings.py'))

    # touch the wsgi file to reload apache
    touch()


def rm_pyc_files():
    """Remove all the old pyc files to prevent stale files being used"""
    require('django_root', provided_by=env.valid_envs)
    with settings(warn_only=True):
        with cd(env.django_root):
            sudo('find . -name \*.pyc | xargs rm')

def link_apache_conf():
    """link the apache.conf file"""
    require('vcs_root', provided_by=env.valid_envs)
    if env.use_apache == False:
        return
    conf_file = os.path.join(env.vcs_root, 'apache', env.environment+'.conf')
    apache_conf = os.path.join('/etc/httpd/conf.d', env.project+'_'+env.environment+'.conf')
    if not files.exists(conf_file):
        utils.abort('No apache conf file found - expected %s' % conf_file)
    if not files.exists(apache_conf):
        sudo('ln -s %s %s' % (conf_file, apache_conf))
    configtest()


def configtest():    
    """ test Apache configuration """
    if env.use_apache:
        sudo('/usr/sbin/httpd -S')


def apache_reload():    
    """ reload Apache on remote host """
    apache_cmd('reload')


def apache_restart():    
    """ restart Apache on remote host """
    apache_cmd('restart')


def apache_cmd(cmd):
    """ run cmd against apache init.d script """
    if env.use_apache:
        sudo('/etc/init.d/httpd %s' % cmd)


