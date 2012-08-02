# This script is to set up various things for our projects. It can be used by:
#
# * developers - setting up their own environment
# * jenkins - setting up the environment and running tests
# * fabric - it will call a copy on the remote server when deploying
#
# The tasks it will do (eventually) include:
#
# * creating, updating and deleting the virtualenv
# * creating, updating and deleting the database (sqlite or mysql)
# * setting up the local_settings stuff
# * running tests
"""This script is to set up various things for our projects. It can be used by:

* developers - setting up their own environment
* jenkins - setting up the environment and running tests
* fabric - it will call a copy on the remote server when deploying

"""

import os, sys
import getpass
import random

# make sure WindowsError is available
import __builtin__
if not hasattr(__builtin__, 'WindowsError'):
    class WindowsError(OSError):
        pass

# import per-project settings
import project_settings

if os.path.exists(os.path.join(os.path.dirname(__file__), 'localtasks.py')):
    import localtasks
else:
    localtasks = None

try:
    # For testing replacement routines for older python compatibility
    # raise ImportError()
    import subprocess
    from subprocess import call as _call_command

    def _capture_command(argv):
        return subprocess.Popen(argv, stdout=subprocess.PIPE).communicate()[0]

except ImportError:
    # this section is for python older than 2.4 - basically for CentOS 4
    # when we have to use it
    def _capture_command(argv):
        command = ' '.join(argv)
        # print "(_capture_command) Executing: %s" % command
        fd = os.popen(command)
        output = fd.read()
        fd.close()
        return output

    # older python - shell arg is ignored, but is legal
    def _call_command(argv, stdin=None, stdout=None, shell=True):
        argv = [i.replace('"', '\"') for i in argv]
        argv = ['"%s"' % i for i in argv]
        command = " ".join(argv)

        if stdin is not None:
            command += " < " + stdin.name

        if stdout is not None:
            command += " > " + stdout.name

        # sys.stderr.write("(_call_command) Executing: %s\n" % command)

        return os.system(command)

try:
    from subprocess import CalledProcessError
except ImportError:
    # the Error does not exist in python 2.4
    class CalledProcessError(Exception):
        """This exception is raised when a process run by check_call() returns
        a non-zero exit status.  The exit status will be stored in the
        returncode attribute."""
        def __init__(self, returncode, cmd):
            self.returncode = returncode
            self.cmd = cmd
        def __str__(self):
            return "Command '%s' returned non-zero exit status %d" % (self.cmd, self.returncode)


def _call_wrapper(argv, **kwargs):
    if env['verbose']:
        if hasattr(argv, '__iter__'):
            command = ' '.join(argv)
        else:
            command = argv
        print "Executing command: %s" % command
    return _call_command(argv, **kwargs)

def _check_call_wrapper(argv, accepted_returncode_list=[0], **kwargs):
    try:
        returncode = _call_wrapper(argv, **kwargs)

        if returncode not in accepted_returncode_list:
            raise CalledProcessError(returncode, argv)
    except WindowsError:
        raise CalledProcessError("Unknown", argv)

env = {}

def _setup_paths():
    """Set up the paths used by other tasks"""
    env['deploy_dir']   = os.path.dirname(__file__)
    # what is the root of the project - one up from this directory
    env['project_dir']  = os.path.abspath(os.path.join(env['deploy_dir'], '..'))
    env['django_dir']   = os.path.join(env['project_dir'], project_settings.django_dir)
    env['ve_dir']       = os.path.join(env['django_dir'], '.ve')
    env['manage_py']    = os.path.join(env['django_dir'], 'manage.py')
    env['project_name'] = project_settings.project_name
    env['project_type'] = project_settings.project_type

    python26 = os.path.join('/', 'usr', 'bin', 'python2.6')
    python27 = os.path.join('/', 'usr', 'bin', 'python2.7')
    generic_python = os.path.join('/', 'usr', 'bin', 'python')
    paths_to_try = (python26, python27, generic_python, sys.executable)
    chosen_python = None
    for python in paths_to_try:
        if os.path.exists(python):
            chosen_python = python
    if chosen_python is None:
        raise Exception("Failed to find a valid Python executable " +
                "in any of these locations: %s" % paths_to_try)
    if env['verbose']:
        print "Using Python from %s" % chosen_python
    env['python_bin'] = chosen_python

def _manage_py(args, cwd=None):
    # for manage.py, always use the system python 2.6
    # otherwise the update_ve will fail badly, as it deletes
    # the virtualenv part way through the process ...
    manage_cmd = [env['python_bin'], env['manage_py']]
    if env['quiet']:
        manage_cmd.append('--verbosity=0')
    if isinstance(args, str):
        manage_cmd.append(args)
    else:
        manage_cmd.extend(args)

    # Allow manual specification of settings file
    if env.has_key('manage_py_settings'):
        manage_cmd.append('--settings=%s' % env['manage_py_settings'])

    if cwd == None:
        cwd = env['django_dir']

    if env['verbose']:
        print 'Executing manage command: %s' % ' '.join(manage_cmd)
    output_lines = []
    try:
        popen = subprocess.Popen(manage_cmd, cwd=cwd, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
    except OSError, e:
        print "Failed to execute command: %s: %s" % (manage_cmd, e)
        raise e
    for line in iter(popen.stdout.readline, ""):
        if env['verbose']:
            print line,
        output_lines.append(line)
    returncode = popen.wait()
    if returncode != 0:
        print "Failed to execute command: %s: returned %s\n%s" % (manage_cmd,
                returncode, "\n".join(output_lines))
        sys.exit(popen.returncode)
    return output_lines


def _create_dir_if_not_exists(dir_path, world_writeable=False, owner=None):
    if not os.path.exists(dir_path):
        _check_call_wrapper(['mkdir', '-p', dir_path])
    if world_writeable:
        _check_call_wrapper(['chmod', '-R', '777', dir_path])
    if owner:
        _check_call_wrapper(['chown', '-R', owner, dir_path])


def _get_django_db_settings(database='default'):
    """
        Args:
            database (string): The database key to use in the 'DATABASES'
                configuration. Override from the default to use a different
                database.
    """
    # import local_settings from the django dir. Here we are adding the django
    # project directory to the path. Note that env['django_dir'] may be more than
    # one directory (eg. 'django/project') which is why we use django_module
    sys.path.append(env['django_dir'])
    import local_settings

    db_user = 'nouser'
    db_pw   = 'nopass'
    db_host = '127.0.0.1'
    db_port = None
    # there are two ways of having the settings:
    # either as DATABASE_NAME = 'x', DATABASE_USER ...
    # or as DATABASES = { 'default': { 'NAME': 'xyz' ... } }
    try:
        db = local_settings.DATABASES[database]
        db_engine = db['ENGINE']
        db_name   = db['NAME']
        if db_engine.endswith('mysql'):
            db_user   = db['USER']
            db_pw     = db['PASSWORD']
            if db.has_key('PORT'):
                db_port = db['PORT']
            if db.has_key('HOST'):
                db_host = db['HOST']

    except (AttributeError, KeyError):
        try:
            db_engine = local_settings.DATABASE_ENGINE
            db_name   = local_settings.DATABASE_NAME
            if db_engine.endswith('mysql'):
                db_user   = local_settings.DATABASE_USER
                db_pw     = local_settings.DATABASE_PASSWORD
                if hasattr(local_settings, 'DATABASE_PORT'):
                    db_port = local_settings.DATABASE_PORT
                if hasattr(local_settings, 'DATABASE_HOST'):
                    db_host = local_settings.DATABASE_HOST
        except AttributeError:
            # we've failed to find the details we need - give up
            print("Failed to find database settings")
            sys.exit(1)
    env['db_port'] = db_port
    env['db_host'] = db_host
    return (db_engine, db_name, db_user, db_pw, db_port, db_host)


def _mysql_exec_as_root(mysql_cmd, root_password=None):
    """ execute a SQL statement using MySQL as the root MySQL user"""
    # do this so that _test_mysql_root_password() can run without
    # getting stuck in a loop
    if not root_password:
        root_password = _get_mysql_root_password()
    mysql_call = ['mysql', '-u', 'root', '-p'+root_password]
    mysql_call += ['--host=%s' % env['db_host']]

    if env['db_port'] != None:
        mysql_call += ['--port=%s' % env['db_port']]
    mysql_call += ['-e']
    _check_call_wrapper(mysql_call + [mysql_cmd])


def _test_mysql_root_password(password):
    """Try a no-op with the root password"""
    try:
        _mysql_exec_as_root('select 1', password)
    except CalledProcessError:
        return False
    return True

def _get_mysql_root_password():
    # first try to read the root password from a file
    # otherwise ask the user
    if not env.has_key('root_pw'):
        root_pw = None
        # first try and get password from file
        root_pw_file = '/root/mysql_root_password'
        try:
            file_exists = _call_wrapper(['sudo', 'test', '-f', root_pw_file])
        except (WindowsError, CalledProcessError):
            file_exists = 1
        if file_exists == 0:
            # note this requires sudoers to work with this - jenkins particularly ...
            root_pw = _capture_command(["sudo", "cat", root_pw_file])
            root_pw = root_pw.rstrip()
            # maybe it is wrong (on developer machine) - check it
            if not _test_mysql_root_password(root_pw):
                if not env['verbose']:
                    print "mysql root password in %s doesn't work" % root_pw_file
                root_pw = None

        # still haven't got it, ask the user
        while not root_pw:
            print "about to ask user for password"
            root_pw = getpass.getpass('Enter MySQL root password:')
            if not _test_mysql_root_password(root_pw):
                if not env['quiet']:
                    print "Sorry, invalid password"
                root_pw = None

        # now we have root password that works
        env['root_pw'] = root_pw

    return env['root_pw']


def clean_ve():
    """Delete the virtualenv so we can start again"""
    _check_call_wrapper(['rm', '-rf', env['ve_dir']])


def clean_db(database='default'):
    """Delete the database for a clean start"""
    # first work out the database username and password
    db_engine, db_name, db_user, db_pw, db_port, db_host = _get_django_db_settings(database=database)
    # then see if the database exists
    if db_engine.endswith('sqlite'):
        # delete sqlite file
        if os.path.isabs(db_name):
            db_path = db_name
        else:
            db_path = os.path.abspath(os.path.join(env['django_dir'], db_name))
        os.remove(db_path)
    elif db_engine.endswith('mysql'):
        # DROP DATABASE
        _mysql_exec_as_root('DROP DATABASE IF EXISTS %s' % db_name)

        test_db_name = 'test_' + db_name
        _mysql_exec_as_root('DROP DATABASE IF EXISTS %s' % test_db_name)


def create_ve():
    """Create the virtualenv"""
    if not env['quiet']:
        print "### Creating/updating virtualenv - this could take some time"
    _manage_py("update_ve")


def update_ve():
    """ Update the virtualenv """
    create_ve()

def create_private_settings():
    """ create private settings file
    - contains generated DB password and secret key"""
    private_settings_file = os.path.join(env['django_dir'],
                                    'private_settings.py')
    if not os.path.exists(private_settings_file):
        if not env['quiet']:
            print "### creating private_settings.py"
        # don't use "with" for compatibility with python 2.3 on whov2hinari
        f = open(private_settings_file, 'w')
        try:
            secret_key = "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)])
            db_password = "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for i in range(12)])

            f.write("SECRET_KEY = '%s'\n" % secret_key)
            f.write("DB_PASSWORD = '%s'\n" % db_password)
        finally:
            f.close()

def link_local_settings(environment):
    """ link local_settings.py.environment as local_settings.py """
    # die if the correct local settings does not exist
    if not env['quiet']:
        print "### creating link to local_settings.py"
    local_settings_env_path = os.path.join(env['django_dir'],
                                    'local_settings.py.'+environment)
    if not os.path.exists(local_settings_env_path):
        print "Could not find file to link to: %s" % local_settings_env_path
        sys.exit(1)

    files_to_remove = ('local_settings.py', 'local_settings.pyc')
    for file in files_to_remove:
        full_path = os.path.join(env['django_dir'], file)
        if os.path.exists(full_path):
            os.remove(full_path)

    source = os.path.join(env['django_dir'], 'local_settings.py.%s' %
        environment)
    target = os.path.join(env['django_dir'], 'local_settings.py')

    if os.name == 'posix':
        os.symlink('local_settings.py.%s' % environment, target)
    elif os.name == 'nt':
        try:
            import win32file
        except ImportError:
            raise Exception("It looks like the PyWin32 extensions are not " +
                "installed")
        if os.path.exists(target):
            os.unlink(target)
        try:
            win32file.CreateSymbolicLink(target, source)
        except NotImplementedError:
            win32file.CreateHardLink(target, source)
    else:
        import shutil
        shutil.copy2(source, target)



def _get_cache_table():
    # import settings from the django dir
    sys.path.append(env['django_dir'])
    import settings
    if not hasattr(settings, 'CACHES'):
        return None
    if not settings.CACHES['default']['BACKEND'].endswith('DatabaseCache'):
        return None
    return settings.CACHES['default']['LOCATION'] 

def update_db(syncdb=True, drop_test_db=True, force_use_migrations=False, database='default'):
    """ create the database, and do syncdb and migrations
    Note that if syncdb is true, then migrations will always be done if one of
    the Django apps has a directory called 'migrations/'
    Args:
        syncdb (bool): whether to run syncdb (aswell as creating database)
        drop_test_db (bool): whether to drop the test database after creation
        force_use_migrations (bool): whether to force migrations, even when no
            migrations/ directories are found.
        database (string): The database value passed to _get_django_db_settings.
    """
    if not env['quiet']:
        print "### Creating and updating the databases"

    # first work out the database username and password
    db_engine, db_name, db_user, db_pw, db_port, db_host = _get_django_db_settings(database=database)

    # then see if the database exists
    if db_engine.endswith('mysql'):
        if not db_exists(db_user, db_pw, db_name, db_port, db_host):
            _mysql_exec_as_root('CREATE DATABASE %s CHARACTER SET utf8' % db_name)
            _mysql_exec_as_root(('GRANT ALL PRIVILEGES ON %s.* TO \'%s\'@\'localhost\' IDENTIFIED BY \'%s\'' %
                (db_name, db_user, db_pw)))

        if not db_exists(db_user, db_pw, 'test_'+db_name, db_port, db_host):
            create_test_db(drop_after_create=drop_test_db, database=database)

    #print 'syncdb: %s' % type(syncdb)
    use_migrations = force_use_migrations
    if env['project_type'] == "django" and syncdb:
        # if we are using the database cache we need to create the table
        # and we need to do it before syncdb
        cache_table = _get_cache_table()
        if cache_table and not db_table_exists(cache_table,
                db_user, db_pw, db_name, db_port, db_host):
            _manage_py(['createcachetable', cache_table])
        # if we are using South we need to do the migrations aswell
        for app in project_settings.django_apps:
            if os.path.exists(os.path.join(env['django_dir'], app, 'migrations')):
                use_migrations = True
        _manage_py(['syncdb', '--noinput'])
        if use_migrations:
            _manage_py(['migrate', '--noinput'])

def db_exists(db_user, db_pw, db_name, db_port, db_host):
    db_exist_call = ['mysql', '-u', db_user, '-p'+db_pw]
    db_exist_call += ['--host=%s' % db_host]

    if db_port != None:
        db_exist_call += ['--port=%s' % db_port]

    db_exist_call += [db_name, '-e', 'quit']
    try:
        _check_call_wrapper(db_exist_call)
        return True
    except CalledProcessError:
        return False

def db_table_exists(table_name, db_user, db_pw, db_name, db_port, db_host):
    table_list_call = ['mysql', '-u', db_user, '-p'+db_pw]
    table_list_call += ['--host=%s' % db_host]

    if db_port != None:
        table_list_call += ['--port=%s' % db_port]

    table_list_call += [db_name, '-e', 'show tables']
    tables = _capture_command(table_list_call)
    table_list = tables.split()
    return table_name in table_list

def create_test_db(drop_after_create=True, database='default'):
    db_engine, db_name, db_user, db_pw, db_port, db_host = _get_django_db_settings(database=database)

    test_db_name = 'test_' + db_name
    _mysql_exec_as_root('CREATE DATABASE %s CHARACTER SET utf8' % test_db_name)
    _mysql_exec_as_root(('GRANT ALL PRIVILEGES ON %s.* TO \'%s\'@\'localhost\' IDENTIFIED BY \'%s\'' %
        (test_db_name, db_user, db_pw)))
    if drop_after_create:
        _mysql_exec_as_root(('DROP DATABASE %s' % test_db_name))

def dump_db(dump_filename='db_dump.sql', for_rsync=False):
    """Dump the database in the current working directory"""
    db_engine, db_name, db_user, db_pw, db_port, db_host = _get_django_db_settings()
    if not db_engine.endswith('mysql'):
        print 'dump_db only knows how to dump mysql so far'
        sys.exit(1)
    dump_cmd = ['/usr/bin/mysqldump', '--user='+db_user, '--password='+db_pw,
                '--host='+db_host]
    if db_port != None:
        dump_cmd.append('--port='+db_port)
    # this option will mean that there will be one line per insert
    # thus making the dump file better for rsync, but slightly bigger
    if for_rsync:
        dump_cmd.append('--skip-extended-insert')
    dump_cmd.append(db_name)

    dump_file = open(dump_filename, 'w')
    if env['verbose']:
        print 'Executing dump command: %s\nSending stdout to %s' % (' '.join(dump_cmd), dump_filename)
    _call_command(dump_cmd, stdout=dump_file)
    dump_file.close()

def restore_db(dump_filename):
    """Restore a database dump file by name"""
    db_engine, db_name, db_user, db_pw, db_port, db_host = _get_django_db_settings()
    if not db_engine.endswith('mysql'):
        print 'restore_db only knows how to restore mysql so far'
        sys.exit(1)
    restore_cmd = ['/usr/bin/mysql', '--user='+db_user, '--password='+db_pw,
                '--host='+db_host]
    if db_port != None:
        restore_cmd.append('--port='+db_port)
    restore_cmd.append(db_name)
    
    dump_file = open(dump_filename, 'r')
    if env['verbose']:
        print 'Executing dump command: %s\nSending stdin to %s' % (' '.join(restore_cmd), dump_filename)
    _call_command(restore_cmd, stdin=dump_file)
    dump_file.close()


def update_git_submodules():
    """If this is a git project then check for submodules and update"""
    git_modules_file = os.path.join(env['project_dir'], '.gitmodules')
    if os.path.exists(git_modules_file):
        if not env['quiet']:
            print "### updating git submodules"
            git_submodule_cmd = 'git submodule update --init'
        else:
            git_submodule_cmd = 'git submodule --quiet update --init'
        _check_call_wrapper(git_submodule_cmd, cwd=env['project_dir'], shell=True)

def setup_db_dumps(dump_dir):
    """ set up mysql database dumps in root crontab """
    if not os.path.isabs(dump_dir):
        print 'dump_dir must be an absolute path, you gave %s' % dump_dir
        sys.exit(1)
    project_name = project_settings.django_dir.split('/')[-1]
    cron_file = os.path.join('/etc', 'cron.daily', 'dump_'+project_name)

    db_engine, db_name, db_user, db_pw, db_port, db_host = _get_django_db_settings()
    if db_engine.endswith('mysql'):
        _create_dir_if_not_exists(dump_dir)
        dump_file_stub = os.path.join(dump_dir, 'daily-dump-')

        # has it been set up already
        cron_set = True
        try:
            _check_call_wrapper('sudo crontab -l | grep mysqldump', shell=True)
        except CalledProcessError:
            cron_set = False

        if cron_set:
            return
        if os.path.exists(cron_file):
            return

        # write something like:
        # 30 1 * * * mysqldump --user=osiaccounting --password=aptivate --host=127.0.0.1 osiaccounting >  /var/osiaccounting/dumps/daily-dump-`/bin/date +\%d`.sql

        # don't use "with" for compatibility with python 2.3 on whov2hinari
        f = open(cron_file, 'w')
        try:
            f.write('#!/bin/sh\n')
            f.write('/usr/bin/mysqldump --user=%s --password=%s --host=%s --port=%s ' %
                    (db_user, db_pw, db_host, db_port))
            f.write('%s > %s' % (db_name, dump_file_stub))
            f.write(r'`/bin/date +\%d`.sql')
            f.write('\n')
        finally:
            f.close()

        os.chmod(cron_file, 0755)


def run_tests(*extra_args):
    """Run the django tests.

    With no arguments it will run all the tests for you apps (as listed in
    project_settings.py), but you can also pass in multiple arguments to run
    the tests for just one app, or just a subset of tests. Examples include:

    ./tasks.py run_tests:myapp
    ./tasks.py run_tests:myapp.ModelTests,myapp.ViewTests.my_view_test
    """
    args = ['test', '-v0']

    if extra_args:
        args += extra_args
    else:
        # default to running all tests
        args += project_settings.django_apps

    _manage_py(args)


def quick_test(*extra_args):
    """Run the django tests with local_settings.py.dev_fasttests

    local_settings.py.dev_fasttests (should) use port 3307 so it will work
    with a mysqld running with a ramdisk, which should be a lot faster. The
    original environment will be reset afterwards.

    With no arguments it will run all the tests for you apps (as listed in
    project_settings.py), but you can also pass in multiple arguments to run
    the tests for just one app, or just a subset of tests. Examples include:

    ./tasks.py quick_test:myapp
    ./tasks.py quick_test:myapp.ModelTests,myapp.ViewTests.my_view_test
    """
    original_environment = _infer_environment()

    link_local_settings('dev_fasttests')
    create_ve()
    update_db()
    run_tests(*extra_args)
    link_local_settings(original_environment)


def _install_django_jenkins():
    """ ensure that pip has installed the django-jenkins thing """
    if not env['quiet']:
        print "### Installing Jenkins packages"
    pip_bin = os.path.join(env['ve_dir'], 'bin', 'pip')
    cmds = [
        [pip_bin, 'install', 'django-jenkins'],
        [pip_bin, 'install', 'pylint'],
        [pip_bin, 'install', 'coverage']]

    for cmd in cmds:
        _check_call_wrapper(cmd)

def _manage_py_jenkins():
    """ run the jenkins command """
    args = ['jenkins', ]
    args += ['--pylint-rcfile', os.path.join(env['project_dir'], 'jenkins', 'pylint.rc')]
    coveragerc_filepath = os.path.join(env['project_dir'], 'jenkins', 'coverage.rc')
    if os.path.exists(coveragerc_filepath):
        args += ['--coverage-rcfile', coveragerc_filepath]
    args += project_settings.django_apps
    if not env['quiet']:
        print "### Running django-jenkins, with args; %s" % args
    _manage_py(args, cwd=env['project_dir'])

def run_jenkins():
    """ make sure the local settings is correct and the database exists """
    env['verbose'] = True
    update_ve()
    _install_django_jenkins()
    create_private_settings()
    link_local_settings('jenkins')
    clean_db()
    update_db()
    _manage_py_jenkins()


def _infer_environment():
    local_settings = os.path.join(env['django_dir'], 'local_settings.py')
    if os.path.exists(local_settings):
        return os.readlink(local_settings).split('.')[-1]
    else:
        print 'no environment set, or pre-existing'
        sys.exit(2)


def deploy(environment=None):
    """Do all the required steps in order"""
    if environment == None:
        environment = _infer_environment()
        if env['verbose']:
            print "Inferred environment as %s" % environment

    create_private_settings()
    link_local_settings(environment)
    update_git_submodules()
    create_ve()
    update_db()

    if hasattr(localtasks, 'post_deploy'):
        localtasks.post_deploy(environment)

    print "\n*** Finished deploying %s for %s." % (
            env['project_name'], environment)

def patch_south():
    """ patch south to fix pydev errors """
    south_db_init = os.path.join(env['ve_dir'],
                'lib/python2.6/site-packages/south/db/__init__.py')
    patch_file = os.path.join(env['deploy_dir'], 'south.patch')
    cmd = ['patch', '-N', '-p0', south_db_init, patch_file]
    _check_call_wrapper(cmd)
