#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
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

# VIRTUAL_ENV will be set if we are already inside a virtualenv (either because
# of standard virtualenv activate, or because go_to_ve() set it).
if 'IGNORE_DOTVE' not in os.environ and 'VIRTUAL_ENV' not in os.environ:
    # if it appears that the virtualenv is out of date then stop here
    updater = ve_mgr.UpdateVE()
    if updater.virtualenv_needs_update():
        print "VirtualEnv need to be updated"
        print 'Run "deploy/bootstrap.py'
        sys.exit(1)

    # now we should enter the virtualenv. We will only get
    # this far if the virtualenv is up to date.
    updater.go_to_ve(__file__, sys.argv[1:])

# run django - the usual manage.py stuff
if __name__ == "__main__":
    sys.path.append(DEPLOY_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    try:
        import settings  # pylint: disable=W402
    except ImportError as e:
        raise ImportError("%s\n\nFailed to import settings module: "
            "does it contain errors? Did you run tasks.py deploy:dev?"
            % e)

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
