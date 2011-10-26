#!/usr/bin/python2.6
#
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
import getopt
import getpass
import subprocess 
import random

# import per-project settings
import project_settings

# are there any local tasks for this project?
try:
    import localtasks
except ImportError:
    localtasks = None

env = {}

def _setup_paths():
    """Set up the paths used by other tasks"""
    env['deploy_dir'] = os.path.dirname(__file__)
    # what is the root of the project - one up from this directory
    env['project_dir'] = os.path.join(env['deploy_dir'], '..')
    env['django_dir']  = os.path.join(env['project_dir'], project_settings.django_dir)
    env['ve_dir']      = os.path.join(env['django_dir'], '.ve')
    env['python_bin']  = os.path.join(env['ve_dir'], 'bin', 'python2.6')
    env['manage_py']   = os.path.join(env['django_dir'], 'manage.py')


def _manage_py(args, cwd=None, supress_output=False):
    # for manage.py, always use the system python 2.6
    # otherwise the update_ve will fail badly, as it deletes
    # the virtualenv part way through the process ...
    manage_cmd = ['/usr/bin/python2.6', env['manage_py']]
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
    popen = subprocess.Popen(manage_cmd, cwd=cwd, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
    for line in iter(popen.stdout.readline, ""):
        if env['verbose'] or not supress_output:
            print line,
        output_lines.append(line)
    returncode = popen.wait()
    if returncode != 0:
        sys.exit(popen.returncode)
    return output_lines


def _get_django_db_settings():
    # import local_settings from the django dir. Here we are adding the django
    # project directory to the path. Note that env['django_dir'] may be more than
    # one directory (eg. 'django/project') which is why we use django_module
    sys.path.append(env['django_dir'])
    import local_settings

    db_user = 'nouser'
    db_pw   = 'nopass'
    db_port = None
    # there are two ways of having the settings:
    # either as DATABASE_NAME = 'x', DATABASE_USER ...
    # or as DATABASES = { 'default': { 'NAME': 'xyz' ... } }
    try:
        db = local_settings.DATABASES['default']
        db_engine = db['ENGINE']
        db_name   = db['NAME']
        if db_engine.endswith('mysql'):
            db_user   = db['USER']
            db_pw     = db['PASSWORD']
            if db.has_key('PORT'):
                db_port = db['PORT']
    except (AttributeError, KeyError):
        try:
            db_engine = local_settings.DATABASE_ENGINE
            db_name   = local_settings.DATABASE_NAME
            if db_engine.endswith('mysql'):
                db_user   = local_settings.DATABASE_USER
                db_pw     = local_settings.DATABASE_PASSWORD
                if hasattr(local_settings, 'DATABASE_PORT'):
                    db_port = local_settings.DATABASE_PORT
        except AttributeError:
            # we've failed to find the details we need - give up
            print("Failed to find database settings")
            sys.exit(1)
    env['db_port'] = db_port
    return (db_engine, db_name, db_user, db_pw, db_port)


def _mysql_exec_as_root(mysql_cmd):
    """ execute a SQL statement using MySQL as the root MySQL user"""
    mysql_call = ['mysql', '-u', 'root', '-p'+_get_mysql_root_password()]
    if env['db_port'] != None:
        mysql_call += ['--host=127.0.0.1', '--port=%s' % env['db_port']]
    mysql_call += ['-e']
    if env['verbose']:
        print 'Executing MySQL command: %s' % ' '.join(mysql_call + [mysql_cmd])
    subprocess.call(mysql_call + [mysql_cmd])


def _get_mysql_root_password():
    # first try to read the root password from a file
    # otherwise ask the user
    if not env.has_key('root_pw'):
        file_exists = subprocess.call(['sudo', 'test', '-f', '/root/mysql_root_password'])
        if file_exists == 0:
            # note this requires sudoers to work with this - jenkins particularly ...
            root_pw = subprocess.Popen(["sudo", "cat", "/root/mysql_root_password"], 
                    stdout=subprocess.PIPE).communicate()[0]
            env['root_pw'] = root_pw.rstrip()
        else:
            env['root_pw'] = getpass.getpass('Enter MySQL root password:')
    return env['root_pw']


def clean_ve():
    """Delete the virtualenv so we can start again"""
    subprocess.call(['rm', '-rf', env['ve_dir']])
    
    
def clean_db():
    """Delete the database for a clean start"""
    # first work out the database username and password
    db_engine, db_name, db_user, db_pw, db_port = _get_django_db_settings()
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
    _manage_py("update_ve")
    
    
def update_ve():
    """ Update the virtualenv """
    create_ve()

def create_private_settings():

    private_settings_file = os.path.join(env['django_dir'], 
                                    'private_settings.py')
    if not os.path.exists(private_settings_file):
    
        with open(private_settings_file, 'w') as f:
            secret_key = "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)])
            db_password = "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for i in range(12)])
            
            f.write("SECRET_KEY = '%s'\n" % secret_key)
            f.write("DB_PASSWORD = '%s'\n" % db_password)
    
def link_local_settings(environment):
    """ link local_settings.py.environment as local_settings.py """
    # die if the correct local settings does not exist
    local_settings_env_path = os.path.join(env['django_dir'], 
                                    'local_settings.py.'+environment)
    if not os.path.exists(local_settings_env_path):
        print "Could not find file to link to: %s" % local_settings_env_path
        sys.exit(1)
    # remove the pyc aswell
    subprocess.call(['rm', 'local_settings.py', 'local_settings.pyc'], cwd=env['django_dir'])
    subprocess.call(['ln', '-s', 'local_settings.py.'+environment, 'local_settings.py'], 
            cwd=env['django_dir'])


def update_db(syncdb=True):
    """ create the database, and do syncdb and migrations (if syncdb==True)"""
    # first work out the database username and password
    db_engine, db_name, db_user, db_pw, db_port = _get_django_db_settings()
    # then see if the database exists
    if db_engine.endswith('mysql'):
        db_exist_call = ['mysql', '-u', db_user, '-p'+db_pw]
        if db_port != None:
            db_exist_call += ['--host=127.0.0.1', '--port=%s' % db_port]
        db_exist_call += [db_name, '-e', 'quit']
        db_exist = subprocess.call(db_exist_call)
        if db_exist != 0:
            # create the database and grant privileges
            _mysql_exec_as_root('CREATE DATABASE %s CHARACTER SET utf8' % db_name)
            _mysql_exec_as_root(('GRANT ALL PRIVILEGES ON %s.* TO \'%s\'@\'localhost\' IDENTIFIED BY \'%s\'' % 
                (db_name, db_user, db_pw)))

            # create the test database, grant privileges and drop it again
            test_db_name = 'test_' + db_name
            _mysql_exec_as_root('CREATE DATABASE %s CHARACTER SET utf8' % test_db_name)
            _mysql_exec_as_root(('GRANT ALL PRIVILEGES ON %s.* TO \'%s\'@\'localhost\' IDENTIFIED BY \'%s\'' % 
                (test_db_name, db_user, db_pw)))
            _mysql_exec_as_root(('DROP DATABASE %s' % test_db_name))
    print 'syncdb: %s' % type(syncdb)
    if syncdb:
        # if we are using South we need to do the migrations aswell
        use_migrations = False
        for app in project_settings.django_apps:
            if os.path.exists(os.path.join(env['django_dir'], app, 'migrations')):
                use_migrations = True
        _manage_py(['syncdb', '--noinput'])
        if use_migrations:
            _manage_py(['migrate', '--noinput'])

def dump_db(dump_filename='db_dump.sql'):
    """Dump the database in the current working directory"""
    project_name = project_settings.django_dir.split('/')[-1]
    db_engine, db_name, db_user, db_pw, db_port = _get_django_db_settings()
    if not db_engine.endswith('mysql'):
        print 'dump_db only knows how to dump mysql so far'
        sys.exit(1)
    dump_cmd = ['/usr/bin/mysqldump', '--user='+db_user, '--password='+db_pw, '--host=127.0.0.1']
    if db_port != None and len(db_port) > 0:
        dump_cmd += ['--port=%s' % db_port]
    dump_cmd += [db_name]
    # open the file to write to
    dump_file = open(dump_filename, 'w')
    if env['verbose']:
        print 'Executing dump command: %s - stdout to %s' % (' '.join(dump_cmd), dump_filename)
    subprocess.call(dump_cmd, stdout=dump_file)
    dump_file.close()


def setup_db_dumps(dump_dir):
    """ set up mysql database dumps in root crontab """
    if not os.path.isabs(dump_dir):
        print 'dump_dir must be an absolute path, you gave %s' % dump_dir
        sys.exit(1)
    project_name = project_settings.django_dir.split('/')[-1]
    cron_file = os.path.join('/etc', 'cron.daily', 'dump_'+project_name)

    db_engine, db_name, db_user, db_pw, db_port = _get_django_db_settings()
    if db_engine.endswith('mysql'):
        if not os.path.exists(dump_dir):
            subprocess.call(['mkdir', '-p', dump_dir])
        dump_file_stub = os.path.join(dump_dir, 'daily-dump-')

        # has it been set up already
        cron_grep = subprocess.call('sudo crontab -l | grep mysqldump', shell=True)
        if cron_grep == 0:
            return
        if os.path.exists(cron_file):
            return

        # write something like:
        # 30 1 * * * mysqldump --user=osiaccounting --password=aptivate --host=127.0.0.1 osiaccounting >  /var/osiaccounting/dumps/daily-dump-`/bin/date +\%d`.sql
        with open(cron_file, 'w') as f:
            f.write('#!/bin/sh\n')
            f.write('/usr/bin/mysqldump --user=%s --password=%s --host=127.0.0.1 ' %
                    (db_user, db_pw))
            if db_port != None:
                f.write('--port=%s ' % db_port)
            f.write('%s > %s' % (db_name, dump_file_stub))
            f.write(r'`/bin/date +\%d`.sql')
            f.write('\n')
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
    pip_bin = os.path.join(env['ve_dir'], 'bin', 'pip')
    cmd = [pip_bin, 'install', '-E', env['ve_dir'], 'django-jenkins']
    subprocess.call(cmd)

def _manage_py_jenkins():
    """ run the jenkins command """
    args = ['jenkins', ]
    args += ['--pylint-rcfile', os.path.join(env['project_dir'], 'jenkins', 'pylint.rc')]
    coveragerc_filepath = os.path.join(env['project_dir'], 'jenkins', 'coverage.rc')
    if os.path.exists(coveragerc_filepath):
        args += ['--coverage-rcfile', coveragerc_filepath]
    args += project_settings.django_apps
    _manage_py(args, cwd=env['project_dir'])

def run_jenkins():
    """ make sure the local settings is correct and the database exists """
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
    
    create_private_settings()
    link_local_settings(environment)
    create_ve()
    update_db()

def patch_south():
    """ patch south to fix pydev errors """
    south_db_init = os.path.join(env['ve_dir'],
                'lib/python2.6/site-packages/south/db/__init__.py')
    patch_file = os.path.join(env['deploy_dir'], 'south.patch')
    cmd = ['patch', '-N', '-p0', south_db_init, patch_file]
    subprocess.call(cmd)
