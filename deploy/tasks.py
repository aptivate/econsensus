#!/usr/bin/env python
# a script to set up the virtualenv so we can use fabric and tasks

import os
from os import path
import sys
import subprocess
from ve_mgr import check_python_version, UpdateVE

# check python version is high enough
check_python_version(2, 6, __file__)

if 'VIRTUAL_ENV' in os.environ:
    ve_dir = os.environ['VIRTUAL_ENV']
else:
    from project_settings import local_vcs_root, relative_ve_dir
    ve_dir = path.join(local_vcs_root, relative_ve_dir)

if not os.path.exists(ve_dir):
    print "Expected virtualenv does not exist"
    print "(required for correct version of fabric and dye)"
    print "Please run './bootstrap.py' to create virtualenv"
    sys.exit(1)

updater = UpdateVE(ve_dir=ve_dir)
if updater.virtualenv_needs_update():
    print "VirtualEnv needs to be updated"
    print 'Run deploy/bootstrap.py'
    sys.exit(1)

# depending on how you've installed dye, you may need to edit this line
tasks = path.join(ve_dir, 'bin', 'tasks.py')

current_dir = path.dirname(__file__)

# call the tasks.py in the virtual env
tasks_call = [tasks]
# tell tasks.py that this directory is where it can find project_settings and
# localtasks (if it exists)
tasks_call += ['--deploydir=' + current_dir]
# add any arguments passed to this script
tasks_call += sys.argv[1:]

if '-v' in sys.argv or '--verbose' in sys.argv:
    print "Running tasks.py in ve: %s" % ' '.join(tasks_call)

# exit with the tasks.py exit code
sys.exit(subprocess.call(tasks_call))
