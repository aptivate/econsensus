#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, subprocess
from os import path

# check python version is high enough
MIN_PYTHON_MAJOR_VERSION = 2
MIN_PYTHON_MINOR_VERSION = 6
PYTHON_EXE = 'python%d.%d' % (MIN_PYTHON_MAJOR_VERSION, MIN_PYTHON_MINOR_VERSION)

if (sys.version_info[0] < MIN_PYTHON_MAJOR_VERSION or
        sys.version_info[1] < MIN_PYTHON_MINOR_VERSION):
    # we use the environ thing to stop recursing if unexpected things happen
    if 'RECALLED_CORRECT_PYTHON' not in os.environ:
        new_env = os.environ.copy()
        new_env['RECALLED_CORRECT_PYTHON'] = 'true'
        try:
            retcode = subprocess.call([PYTHON_EXE, __file__] + sys.argv[1:],
                    env=new_env)
            sys.exit(retcode)
        except OSError:
            print >> sys.stderr, "You must use python %d.%d or later, you are using %d.%d" % (
                    MIN_PYTHON_MAJOR_VERSION, MIN_PYTHON_MINOR_VERSION,
                    sys.version_info[0], sys.version_info[1])
            print >> sys.stderr, "Could not find %s in path" % PYTHON_EXE
            sys.exit(1)
    else:
        print >> sys.stderr, "You must use python %d.%d or later, you are using %d.%d" % (
                MIN_PYTHON_MAJOR_VERSION, MIN_PYTHON_MINOR_VERSION,
                sys.version_info[0], sys.version_info[1])
        print >> sys.stderr, "Try doing '%s ./manage.py somecommand' instead" \
                % PYTHON_EXE
        sys.exit(1)

# ignore the usual virtualenv
# note that for runserver Django will start a child process, so that it
# can kill and restart the child process. So we use the environment to pass
# the argument along.
if '--ignore-ve' in sys.argv:
    sys.argv.remove('--ignore-ve')
    os.environ['IGNORE_DOTVE'] = 'true'

if 'IGNORE_DOTVE' not in os.environ:
    import shutil
    PROJECT_ROOT = path.abspath(path.dirname(__file__))
    DEPLOY_DIR = path.abspath(path.join(PROJECT_ROOT, '..', '..', 'deploy'))

    REQUIREMENTS = path.join(DEPLOY_DIR, 'pip_packages.txt')
    VE_ROOT = path.join(PROJECT_ROOT, '.ve')
    VE_TIMESTAMP = path.join(VE_ROOT, 'timestamp')

    if not path.exists(REQUIREMENTS):
        print >> sys.stderr, "Could not find requirements: file %s" % REQUIREMENTS
        sys.exit(1)

    def update_ve_timestamp():
        file(VE_TIMESTAMP, 'w').close()

    def virtualenv_needs_update():
        # timestamp of last modification of .ve/ directory
        ve_dir_mtime = path.exists(VE_ROOT) and path.getmtime(VE_ROOT) or 0
        # timestamp of last modification of .ve/timestamp file (touched by this
        # script
        ve_timestamp_mtime = path.exists(VE_TIMESTAMP) and path.getmtime(VE_TIMESTAMP) or 0
        # timestamp of requirements file (pip_packages.txt)
        reqs_timestamp = path.getmtime(REQUIREMENTS)
        # if the requirements file is newer than the virtualenv directory,
        # then the virtualenv needs updating
        if ve_dir_mtime < reqs_timestamp:
            return True
        # if the requirements file is newer than the virtualenv timestamp file,
        # then the virtualenv needs updating
        elif ve_timestamp_mtime < reqs_timestamp:
            return True
        else:
            return False

    def go_to_ve():
        """
        If running inside virtualenv already, then just return and carry on.

        If not inside the virtualenv then call the virtualenv python, pass it
        this file and all the arguments to it, so this file will be run inside
        the virtualenv.
        """
        if 'IN_VIRTUALENV' not in os.environ:
            if sys.platform == 'win32':
                python = path.join(VE_ROOT, 'Scripts', 'python.exe')
            else:
                python = path.join(VE_ROOT, 'bin', 'python')

            # add environment variable to say we are now in virtualenv
            new_env = os.environ.copy()
            new_env['IN_VIRTUALENV'] = 'true'
            retcode = subprocess.call([python, __file__] + sys.argv[1:],
                    env=new_env)
            sys.exit(retcode)

    # manually update virtualenv?
    update_ve = 'update_ve' in sys.argv or 'update_ve_quick' in sys.argv
    # destroy the old virtualenv so we have a clean virtualenv?
    destroy_old_ve = 'update_ve' in sys.argv
    # check if virtualenv needs updating and only proceed if it is required
    update_required = virtualenv_needs_update()
    # or just do the update anyway
    force_update = '--force' in sys.argv

    # we've been told to update the virtualenv AND
    # EITHER it needs an update OR the update is forced
    if update_ve:
        if not update_required and not force_update:
            print "VirtualEnv does not need to be updated"
            print "use --force to force an update"
            sys.exit(0)
        # if we need to create the virtualenv, then we must do that from
        # outside the virtualenv. The code inside this if statement will only
        # be run outside the virtualenv.
        if destroy_old_ve and path.exists(VE_ROOT):
            shutil.rmtree(VE_ROOT)
        if not path.exists(VE_ROOT):
            import virtualenv
            virtualenv.logger = virtualenv.Logger(consumers=[])
            #virtualenv.create_environment(VE_ROOT, site_packages=True)
            virtualenv.create_environment(VE_ROOT, site_packages=False)

        # install the pip requirements and exit
        pip_path = path.join(VE_ROOT, 'bin', 'pip')
        # use cwd to allow relative path specs in requirements file, e.g. ../tika
        pip_retcode = subprocess.call([pip_path, 'install',
                '--requirement=%s' % REQUIREMENTS ],
                cwd=os.path.dirname(REQUIREMENTS))
        if pip_retcode == 0:
            update_ve_timestamp()
        sys.exit(pip_retcode)
    # else if it appears that the virtualenv is out of date:
    elif update_required:
        print "VirtualEnv need to be updated"
        print 'Run "./manage.py update_ve" (or "./manage.py update_ve_quick")'
        sys.exit(1)

    # now we should enter the virtualenv. We will only get
    # this far if the virtualenv is up to date.
    go_to_ve()

# run django - the usual manage.py stuff
if __name__ == "__main__":
    sys.path.append(DEPLOY_DIR)
    from project_settings import project_name
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    try:
        import settings
    except ImportError as e:
        raise ImportError("%s\n\nFailed to import settings module: "
            "does it contain errors? Did you run tasks.py deploy:dev?"
            % e)

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
