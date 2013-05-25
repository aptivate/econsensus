#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from os import path

PROJECT_ROOT = path.abspath(path.dirname(__file__))
DEPLOY_DIR = path.abspath(path.join(PROJECT_ROOT, os.pardir, os.pardir, 'deploy'))
sys.path.append(DEPLOY_DIR)
import ve_mgr

# check python version is high enough
ve_mgr.check_python_version(2, 6, __file__)

# ignore the usual virtualenv
# note that for runserver Django will start a child process, so that it
# can kill and restart the child process. So we use the environment to pass
# the argument along.
if '--ignore-ve' in sys.argv:
    sys.argv.remove('--ignore-ve')
    os.environ['IGNORE_DOTVE'] = 'true'

if 'IGNORE_DOTVE' not in os.environ:
    try:
        from project_settings import ve_dir
    except ImportError:
        print >> sys.stderr, "could not find ve_dir in project_settings.py"
        sys.exit(1)

    def go_to_ve():
        """
        If running inside virtualenv already, then just return and carry on.

        If not inside the virtualenv then call the virtualenv python, pass it
        this file and all the arguments to it, so this file will be run inside
        the virtualenv.
        """
        if 'IN_VIRTUALENV' not in os.environ:
            if sys.platform == 'win32':
                python = path.join(ve_dir, 'Scripts', 'python.exe')
            else:
                python = path.join(ve_dir, 'bin', 'python')

            # add environment variable to say we are now in virtualenv
            new_env = os.environ.copy()
            new_env['IN_VIRTUALENV'] = 'true'
            retcode = subprocess.call([python, __file__] + sys.argv[1:],
                    env=new_env)
            sys.exit(retcode)

    updater = ve_mgr.UpdateVE()
    # manually update virtualenv?
    update_ve = 'update_ve' in sys.argv or 'update_ve_quick' in sys.argv
    # destroy the old virtualenv so we have a clean virtualenv?
    destroy_old_ve = 'update_ve' in sys.argv
    # check if virtualenv needs updating and only proceed if it is required
    update_required = updater.virtualenv_needs_update()
    # or just do the update anyway
    force_update = '--force' in sys.argv

    # we've been told to update the virtualenv AND
    # EITHER it needs an update OR the update is forced
    if update_ve:
        if not update_required and not force_update:
            print "VirtualEnv does not need to be updated"
            print "use --force to force an update"
            sys.exit(0)
        updater.update_ve()

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
