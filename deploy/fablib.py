import os
import getpass
import time

from fabric.context_managers import cd, hide, settings
from fabric.operations import require, prompt, get, run, sudo, local
from fabric.state import env
from fabric.contrib import files
from fabric import utils

import helper as h

def _setup_paths(project_settings):
    # first merge in variables from project_settings - but ignore __doc__ etc
    user_settings = [x for x in vars(project_settings).keys() if not x.startswith('__')]
    for setting in user_settings:
        env[setting] = vars(project_settings)[setting]

    # allow for project_settings having set up some of these differently
    h.set_dict_if_not_set(env, 'verbose',      False)
    h.set_dict_if_not_set(env, 'use_sudo',     True)
    h.set_dict_if_not_set(env, 'cvs_rsh',      'CVS_RSH="ssh"')
    h.set_dict_if_not_set(env, 'branch',       'master')
    h.set_dict_if_not_set(env, 'project_root', os.path.join(env.server_home, env.project_dir))
    h.set_dict_if_not_set(env, 'vcs_root',     os.path.join(env.project_root, 'dev'))
    h.set_dict_if_not_set(env, 'prev_root',    os.path.join(env.project_root, 'previous'))
    h.set_dict_if_not_set(env, 'dump_dir',     os.path.join(env.project_root, 'dbdumps'))
    h.set_dict_if_not_set(env, 'deploy_root',  os.path.join(env.vcs_root, 'deploy'))
    h.set_dict_if_not_set(env, 'settings',     '%(project_name)s.settings' % env)

    if env.project_type == "django":
        h.set_dict_if_not_set(env, 'django_relative_dir', env.project_name)
        h.set_dict_if_not_set(env, 'django_root', os.path.join(env.vcs_root, env.django_relative_dir))

    if env.use_virtualenv:
        h.set_dict_if_not_set(env, 'virtualenv_root', os.path.join(env.django_root, '.ve'))

    python26 = os.path.join('/', 'usr', 'bin', 'python2.6')
    if os.path.exists(python26):
        h.set_dict_if_not_set(env, 'python_bin', python26)
    else:
        h.set_dict_if_not_set(env, 'python_bin', os.path.join('/', 'usr', 'bin', 'python'))

    h.set_dict_if_not_set(env, 'tasks_bin',
            env.python_bin + ' ' + os.path.join(env.deploy_root, 'tasks.py'))
    h.set_dict_if_not_set(env, 'local_tasks_bin',
            env.python_bin + ' ' + os.path.join(os.path.dirname(__file__), 'tasks.py'))

    # valid environments - used for require statements in fablib
    env.valid_envs = env.host_list.keys()

    # work out if we're based on redhat or centos
    # TODO: look up stackoverflow question about this.
    if files.exists('/etc/redhat-release'):
        env.linux_type = 'redhat'
    elif files.exists('/etc/debian_version'):
        env.linux_type = 'debian'
    else:
        # TODO: should we print a warning here?
        env.linux_type = 'unknown'


def _tasks(tasks_args, verbose=False):
    require('tasks_bin', provided_by=env.valid_envs)
    tasks_cmd = env.tasks_bin
    if env.verbose or verbose:
        tasks_cmd += ' -v'
    sudo_or_run(tasks_cmd + ' ' + tasks_args)

def _get_svn_user_and_pass():
    if not env.has_key('svnuser') or len(env.svnuser) == 0:
        # prompt user for username
        prompt('Enter SVN username:', 'svnuser')
    if not env.has_key('svnpass') or len(env.svnpass) == 0:
        # prompt user for password
        env.svnpass = getpass.getpass('Enter SVN password:')


def verbose(verbose=True):
    """Set verbose output"""
    env.verbose = verbose


def deploy_clean(revision=None):
    """ delete the entire install and do a clean install """
    if env.environment == 'production':
        utils.abort('do not delete the production environment!!!')
    require('project_root', provided_by=env.valid_envs)
    # TODO: dump before cleaning database?
    with settings(warn_only=True):
        webserver_cmd('stop')
    clean_db()
    clean_files()
    deploy(revision)

def clean_files():
    sudo_or_run('rm -rf %s' % env.project_root)

def _create_dir_if_not_exists(path):
    if not files.exists(path):
        sudo_or_run('mkdir -p %s' % path)

def deploy(revision=None, keep=None):
    """ update remote host environment (virtualenv, deploy, update)

    It takes two arguments:

    * revision is the VCS revision ID to checkout (if not specified then
      the latest will be checked out)
    * keep is the number of old versions to keep around for rollback (default
      5)"""
    require('project_root', provided_by=env.valid_envs)
    check_for_local_changes()

    _create_dir_if_not_exists(env.project_root)

    if files.exists(env.vcs_root):
        create_copy_for_rollback(keep)

    # we only have to stop the webserver after creating the rollback copy
    with settings(warn_only=True):
        webserver_cmd('stop')
    checkout_or_update(revision)

    # Use tasks.py deploy:env to actually do the deployment, including
    # creating the virtualenv if it thinks it necessary, ignoring
    # env.use_virtualenv as tasks.py knows nothing about it.
    _tasks('deploy:' + env.environment)

    if env.project_type == "django":
        rm_pyc_files()
        if env.environment == 'production':
            setup_db_dumps()

    link_webserver_conf()
    webserver_cmd('start')

def set_up_celery_daemon():
    require('vcs_root', provided_by=env)
    for command in ('celerybeat', 'celeryd'):
        celery_run_script_location = os.path.join(env['vcs_root'],
                                                  'celery', 'init', command)
        celery_run_script_destination = os.path.join('/etc', 'init.d')
        celery_run_script = os.path.join(celery_run_script_destination,
                                         command)
        celery_configuration_location = os.path.join(env['vcs_root'],
                                                  'celery', 'config', command)
        celery_configuration_destination = os.path.join('/etc', 'default')

        sudo_or_run(" ".join(['cp', celery_run_script_location,
                               celery_run_script_destination]))

        sudo_or_run(" ".join(['chmod', '+x', celery_run_script]))

        sudo_or_run(" ".join(['cp', celery_configuration_location,
                               celery_configuration_destination]))
        sudo_or_run('/etc/init.d/%s restart' % command)

def create_copy_for_rollback(keep):
    """Copy the current version out of the way so we can rollback to it if required."""
    require('prev_root', 'vcs_root', provided_by=env.valid_envs)
    # create directory for it
    prev_dir = os.path.join(env.prev_root, time.strftime("%Y-%m-%d_%H-%M-%S"))
    _create_dir_if_not_exists(prev_dir)
    # cp -a
    sudo_or_run('cp -a %s %s' % (env.vcs_root, prev_dir))
    if (env.project_type == 'django' and
            files.exists(os.path.join(env.django_root, 'local_settings.py'))):
        # dump database (provided local_settings has been set up properly)
        with cd(prev_dir):
            # just in case there is some other reason why the dump fails
            with settings(warn_only=True):
                _tasks('dump_db')
    if keep == None or int(keep) > 0:
        delete_old_versions(keep)


def delete_old_versions(keep=None):
    """Delete old rollback directories, keeping the last "keep" (default 5)"."""
    require('prev_root', provided_by=env.valid_envs)
    # the -1 argument ensures one directory per line
    prev_versions = run('ls -1 ' + env.prev_root).split('\n')
    if keep == None:
        if env.has_key('versions_to_keep'):
            keep = env.versions_to_keep
        else:
            keep = 5
    versions_to_keep = -1 * int(keep)
    prev_versions_to_delete = prev_versions[:versions_to_keep]
    for version_to_delete in prev_versions_to_delete:
        sudo_or_run('rm -rf ' + os.path.join(env.prev_root,
                                             version_to_delete.strip()))


def list_previous():
    """List the previous versions available to rollback to."""
    # could also determine the VCS revision number
    require('prev_root', provided_by=env.valid_envs)
    run('ls ' + env.prev_root)


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
    require('prev_root', 'vcs_root', provided_by=env.valid_envs)
    if migrate and restore_db:
        utils.abort('rollback cannot do both migrate and restore_db')
    if migrate:
        utils.abort("rollback: haven't worked out how to do migrate yet ...")

    if version == 'last':
        # get the latest directory from prev_dir
        # list directories in env.prev_root, use last one
        version = run('ls ' + env.prev_root).split('\n')[-1]
    # check version specified exists
    rollback_dir_base = os.path.join(env.prev_root, version)
    rollback_dir = os.path.join(rollback_dir_base, 'dev')
    if not files.exists(rollback_dir):
        utils.abort("Cannot rollback to version %s, it does not exist, use list_previous to see versions available" % version)

    webserver_cmd("stop")
    # first copy this version out of the way
    create_copy_for_rollback(-1)
    if migrate:
        # run the south migrations back to the old version
        # but how to work out what the old version is??
        pass
    if restore_db:
        # feed the dump file into mysql command
        with cd(rollback_dir_base):
            _tasks('load_dbdump')
    # delete everything - don't want stray files left over
    sudo_or_run('rm -rf %s' % env.vcs_root)
    # cp -a from rollback_dir to vcs_root
    sudo_or_run('cp -a %s %s' % (rollback_dir, env.vcs_root))
    webserver_cmd("start")


def local_test():
    """ run the django tests on the local machine """
    require('project_name')
    with cd(os.path.join("..", env.project_name)):
        local("python " + env.test_cmd, capture=False)


def remote_test():
    """ run the django tests remotely - staging only """
    require('django_root', 'python_bin', provided_by=env.valid_envs)
    if env.environment == 'production':
        utils.abort('do not run tests on the production environment')
    with cd(env.django_root):
        sudo_or_run(env.python_bin + env.test_cmd)

def version():
    """ return the deployed VCS revision and commit comments"""
    require('project_root', 'repo_type', 'vcs_root', 'repository',
        provided_by=env.valid_envs)
    if env.repo_type == "git":
        with cd(env.vcs_root):
            sudo_or_run('git log | head -5')
    elif env.repo_type == "svn":
        _get_svn_user_and_pass()
        with cd(env.vcs_root):
            with hide('running'):
                cmd = 'svn log --non-interactive --username %s --password %s | head -4' % (env.svnuser, env.svnpass)
                sudo_or_run(cmd)
    else:
        utils.abort('Unsupported repo type: %s' % (env.repo_type))

def check_for_local_changes():
    """ check if there are local changes on the remote server """
    require('repo_type', 'vcs_root', provided_by=env.valid_envs)
    status_cmd = {
            'svn': 'svn status --quiet',
            'git': 'git status --short',
            'cvs': '#not worked out yet'
            }
    if env.repo_type == 'cvs':
        print "TODO: write CVS status command"
        return
    if files.exists(os.path.join(env.vcs_root, "." + env.repo_type)):
        with cd(env.vcs_root):
            status = sudo_or_run(status_cmd[env.repo_type])
            if status:
                print 'Found local changes on %s server' % env.environment
                print status
                cont = prompt('Would you like to continue with deployment? (yes/no)',
                        default='no', validate=r'^yes|no$')
                if cont == 'no':
                    utils.abort('Aborting deployment')

def checkout_or_update(revision=None):
    """ checkout or update the project from version control.

    This command works with svn, git and cvs repositories.

    You can also specify a revision to checkout, as an argument."""
    require('project_root', 'repo_type', 'vcs_root', 'repository',
        provided_by=env.valid_envs)
    checkout_fn = {
            'cvs': _checkout_or_update_cvs,
            'svn': _checkout_or_update_svn,
            'git': _checkout_or_update_git,
            }
    if env.repo_type.lower() in checkout_fn:
        checkout_fn[env.repo_type](revision)
    else:
        utils.abort('Unsupported VCS: %s' % env.repo_type.lower())

def _checkout_or_update_svn(revision=None):
    # function to ask for svnuser and svnpass
    _get_svn_user_and_pass()
    # if the .svn directory exists, do an update, otherwise do
    # a checkout
    cmd = 'svn %s --non-interactive --no-auth-cache --username %s --password %s'
    if files.exists(os.path.join(env.vcs_root, ".svn")):
        cmd = cmd % ('update', env.svnuser, env.svnpass)
        if revision:
            cmd += " --revision " + revision
        with cd(env.vcs_root):
            with hide('running'):
                sudo_or_run(cmd)
    else:
        cmd = cmd + " %s %s"
        cmd = cmd % ('checkout', env.svnuser, env.svnpass, env.repository, env.vcs_root)
        if revision:
            cmd += "@" + revision
        with cd(env.project_root):
            with hide('running'):
                sudo_or_run(cmd)

def _checkout_or_update_git(revision=None):
    # if the .git directory exists, do an update, otherwise do
    # a clone
    if files.exists(os.path.join(env.vcs_root, ".git")):
        with cd(env.vcs_root):
            sudo_or_run('git remote rm origin')
            sudo_or_run('git remote add origin %s' % env.repository)
            # fetch now, merge later (if on branch)
            sudo_or_run('git fetch origin')
    else:
        with cd(env.project_root):
            sudo_or_run('git clone -b %s %s %s' %
                    (env.branch, env.repository, env.vcs_root))
    if revision == None:
        # no revision
        # if on branch then merge, otherwise just print a warning
        with cd(env.vcs_root):
            with settings(warn_only=True):
                branch = sudo_or_run('git rev-parse --abbrev-ref HEAD')
            if branch != 'HEAD':
                # we are on a branch
                stash_result = sudo_or_run('git stash')
                sudo_or_run('git merge origin/%s' % branch)
                # if we did a stash, now undo it
                if not stash_result.startswith("No local changes"):
                    sudo_or_run('git stash pop')
            else:
                # not on a branch - just print a warning
                utils.warn('The server git repository is not on a branch')
                utils.warn('No checkout or merge has been done - you should probably')
                utils.warn('redeploy and specify a branch or revision to checkout.')
    else:
        with cd(env.vcs_root):
            stash_result = sudo_or_run('git stash')
            sudo_or_run('git checkout %s' % revision)
            # check if revision is a branch, and do a merge if it is
            with settings(warn_only=True):
                rev_is_branch = sudo_or_run('git branch -r | grep %s' % revision)
            if rev_is_branch.succeeded:
                sudo_or_run('git merge origin/%s' % branch)
            # if we did a stash, now undo it
            if not stash_result.startswith("No local changes"):
                sudo_or_run('git stash pop')
    if files.exists(os.path.join(env.vcs_root, ".gitmodules")):
        with cd(env.vcs_root):
            sudo_or_run('git submodule update --init')

def _checkout_or_update_cvs(revision):
    if files.exists(env.vcs_root):
        with cd(env.vcs_root):
            sudo_or_run('CVS_RSH="ssh" cvs update -d -P')
    else:
        if env.has_key('cvs_user'):
            user_spec = env.cvs_user + "@"
        else:
            user_spec = ""

        with cd(env.project_root):
            cvs_options = '-d:%s:%s%s:%s' % (env.cvs_connection_type,
                                             user_spec,
                                             env.repository,
                                             env.repo_path)
            command_options = '-d %s' % env.vcs_root

            if revision is not None:
                command_options += ' -r ' + revision

            sudo_or_run('%s cvs %s checkout %s %s' % (env.cvs_rsh, cvs_options,
                                                      command_options,
                                                      env.cvs_project))

def sudo_or_run(command):
    if env.use_sudo:
        return sudo(command)
    else:
        return run(command)


def update_requirements():
    """ update external dependencies on remote host """
    _tasks('update_ve')

def collect_static_files():
    """ coolect static files in the 'static' directory """
    require('tasks_bin', provided_by=env.valid_envs)
    sudo(env.tasks_bin + ' collect_static')

def clean_db(revision=None):
    """ delete the entire database """
    if env.environment == 'production':
        utils.abort('do not delete the production database!!!')
    _tasks("clean_db")

def get_remote_dump(filename='/tmp/db_dump.sql', local_filename='./db_dump.sql',
        rsync=True):
    """ do a remote database dump and copy it to the local filesystem """
    # future enhancement, do a mysqldump --skip-extended-insert (one insert
    # per line) and then do rsync rather than get() - less data transferred on
    # however rsync might need ssh keys etc
    require('user', 'host', provided_by=env.valid_envs)
    if rsync:
        _tasks('dump_db:' + filename + ',for_rsync=true')
        local("rsync -vz -e 'ssh -p %s' %s@%s:%s %s" % (env.port,
            env.user, env.host, filename, local_filename))
    else:
        _tasks('dump_db:' + filename)
        get(filename, local_path=local_filename)
    sudo_or_run('rm ' + filename)

def get_remote_dump_and_load(filename='/tmp/db_dump.sql',
        local_filename='./db_dump.sql', keep_dump=True, rsync=True):
    """ do a remote database dump, copy it to the local filesystem and then
    load it into the local database """
    get_remote_dump(filename=filename, local_filename=local_filename, rsync=rsync)
    local(env.local_tasks_bin + ' restore_db:' + local_filename)
    if not keep_dump:
        local('rm ' + local_filename)

def update_db(force_use_migrations=False):
    """ create and/or update the database, do migrations etc """
    _tasks('update_db:force_use_migrations=%s' % force_use_migrations)

def setup_db_dumps():
    """ set up mysql database dumps """
    require('dump_dir', provided_by=env.valid_envs)
    _tasks('setup_db_dumps:' + env.dump_dir)

def touch():
    """ touch wsgi file to trigger reload """
    require('vcs_root', provided_by=env.valid_envs)
    wsgi_dir = os.path.join(env.vcs_root, 'wsgi')
    sudo_or_run('touch ' + os.path.join(wsgi_dir, 'wsgi_handler.py'))

def rm_pyc_files():
    """Remove all the old pyc files to prevent stale files being used"""
    require('django_root', provided_by=env.valid_envs)
    with settings(warn_only=True):
        with cd(env.django_root):
            sudo_or_run('find . -name \*.pyc | xargs rm')

def link_webserver_conf():
    """link the webserver conf file"""
    require('vcs_root', provided_by=env.valid_envs)
    if env.webserver == None:
        return
    conf_file = os.path.join(env.vcs_root, env.webserver, env.environment+'.conf')
    if not files.exists(conf_file):
        utils.abort('No %s conf file found - expected %s' %
                (env.webserver, conf_file))
    webserver_conf = _webserver_conf_path()
    if not files.exists(webserver_conf):
        sudo_or_run('ln -s %s %s' % (conf_file, webserver_conf))

    # debian has sites-available/sites-enabled split with links
    if env.linux_type == 'debian':
        webserver_conf_enabled = webserver_conf.replace('available', 'enabled')
        sudo_or_run('ln -s %s %s' % (webserver_conf, webserver_conf_enabled))
    webserver_configtest()

def _webserver_conf_path():
    webserver_conf_dir = {
            'apache_redhat': '/etc/httpd/conf.d',
            'apache_debian': '/etc/apache2/sites-available',
            }
    key = env.webserver + '_' + env.linux_type
    if key in webserver_conf_dir:
        return os.path.join(webserver_conf_dir[key], 
                env.project_name+'_'+env.environment+'.conf')
    else:
        utils.abort('webserver %s is not supported (linux type %s)' %
                (env.webserver, env.linux_type))

def webserver_configtest():
    """ test webserver configuration """
    tests = {
            'apache_redhat': '/usr/sbin/httpd -S',
            'apache_debian': '/usr/sbin/apache2ctl -S',
            }
    if env.webserver:
        key = env.webserver + '_' + env.linux_type
        if key in tests:
            sudo(tests[key])
        else:
            utils.abort('webserver %s is not supported (linux type %s)' %
                    (env.webserver, env.linux_type))


def webserver_reload():
    """ reload webserver on remote host """
    webserver_cmd('reload')


def webserver_restart():
    """ restart webserver on remote host """
    webserver_cmd('restart')


def webserver_cmd(cmd):
    """ run cmd against webserver init.d script """
    cmd_strings = {
            'apache_redhat': '/etc/init.d/httpd',
            'apache_debian': '/etc/init.d/apache2',
            }
    if env.webserver:
        key = env.webserver + '_' + env.linux_type
        if key in cmd_strings:
            sudo(cmd_strings[key] + ' ' + cmd)
        else:
            utils.abort('webserver %s is not supported' % env.webserver)


