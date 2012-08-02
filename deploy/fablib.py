import os
import getpass
import time

from fabric.api import *
from fabric.contrib import files
from fabric import utils

def _set_dict_if_not_set(thedict, key, value):
    if key not in thedict:
        thedict[key] = value

def _setup_path():
    # allow for the fabfile having set up some of these differently
    _set_dict_if_not_set(env, 'verbose',      False)
    _set_dict_if_not_set(env, 'use_sudo',     True)
    _set_dict_if_not_set(env, 'cvs_rsh',      'CVS_RSH="ssh"')
    _set_dict_if_not_set(env, 'branch',       'master')
    _set_dict_if_not_set(env, 'project_root', os.path.join(env.home, env.project_dir))
    _set_dict_if_not_set(env, 'vcs_root',     os.path.join(env.project_root, 'dev'))
    _set_dict_if_not_set(env, 'prev_root',    os.path.join(env.project_root, 'previous'))
    _set_dict_if_not_set(env, 'dump_dir',     os.path.join(env.project_root, 'dbdumps'))
    _set_dict_if_not_set(env, 'deploy_root',  os.path.join(env.vcs_root, 'deploy'))
    _set_dict_if_not_set(env, 'settings',     '%(project)s.settings' % env)

    if env.project_type == "django":
        _set_dict_if_not_set(env, 'django_dir', env.project)
        _set_dict_if_not_set(env, 'django_root', os.path.join(env.vcs_root, env.django_dir))

    if env.use_virtualenv:
        _set_dict_if_not_set(env, 'virtualenv_root', os.path.join(env.django_root, '.ve'))

    python26 = os.path.join('/', 'usr', 'bin', 'python2.6')
    if os.path.exists(python26):
        _set_dict_if_not_set(env, 'python_bin', python26)
    else:
        _set_dict_if_not_set(env, 'python_bin', os.path.join('/', 'usr', 'bin', 'python'))

    _set_dict_if_not_set(env, 'tasks_bin',
            env.python_bin + ' ' + os.path.join(env.deploy_root, 'tasks.py'))
    _set_dict_if_not_set(env, 'local_tasks_bin',
            env.python_bin + ' ' + os.path.join(os.path.dirname(__file__), 'tasks.py'))


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
    require('project_root', provided_by=env.valid_non_prod_envs)
    # TODO: dump before cleaning database?
    with settings(warn_only=True):
        apache_cmd('stop')
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

    # we only have to stop apache after creating the rollback copy
    with settings(warn_only=True):
        apache_cmd('stop')
    checkout_or_update(revision)
    if env.use_virtualenv:
        update_requirements()

    # if we're going to call tasks.py then this has to be done first:
    create_private_settings()
    link_local_settings()

    update_db()


    if env.project_type == "django":
        rm_pyc_files()
        if env.environment == 'production':
            setup_db_dumps()

    link_apache_conf()
    apache_cmd('start')

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

    apache_cmd("stop")
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
    apache_cmd("start")


def local_test():
    """ run the django tests on the local machine """
    require('project')
    with cd(os.path.join("..", env.project)):
        local("python " + env.test_cmd, capture=False)


def remote_test():
    """ run the django tests remotely - staging only """
    require('django_root', 'python_bin', 'test_cmd', provided_by=env.valid_non_prod_envs)
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
    if env.repo_type == "svn":
        _checkout_or_update_svn(revision)
    elif env.repo_type == "git":
        _checkout_or_update_git(revision)
    elif env.repo_type == "cvs":
        _checkout_or_update_cvs(revision)

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
                warn('The server git repository is not on a branch')
                warn('No checkout or merge has been done - you should probably')
                warn('redeploy and specify a branch or revision to checkout.')
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

def create_private_settings():
    _tasks('create_private_settings')

def link_local_settings():
    """link the local_settings.py file for this environment"""
    _tasks('link_local_settings:' + env.environment)

    # check that settings imports local_settings, as it always should,
    # and if we forget to add that to our project, it could cause mysterious
    # failures
    if env.project_type == "django":
        run('grep -q "local_settings" %s' %
            os.path.join(env.django_root, 'settings.py'))

        # touch the wsgi file to reload apache
        touch()


def rm_pyc_files():
    """Remove all the old pyc files to prevent stale files being used"""
    require('django_root', provided_by=env.valid_envs)
    with settings(warn_only=True):
        with cd(env.django_root):
            sudo_or_run('find . -name \*.pyc | xargs rm')

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
        sudo_or_run('ln -s %s %s' % (conf_file, apache_conf))
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


