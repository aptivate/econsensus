#!/usr/bin/env python
# a script to set up the virtualenv so we can use fabric and tasks

import os
from os import path
import sys
import subprocess
from ve_mgr import check_python_version, find_package_dir_in_ve, UpdateVE

# check python version is high enough
check_python_version(2, 6, __file__)

if 'VIRTUAL_ENV' in os.environ:
    ve_dir = os.environ['VIRTUAL_ENV']
else:
    from project_settings import local_vcs_root, relative_ve_dir
    ve_dir = path.join(local_vcs_root, relative_ve_dir)

if not path.exists(ve_dir):
    print "Expected virtualenv does not exist"
    print "(required for correct version of fabric and dye)"
    print "Please run './bootstrap.py' to create virtualenv"
    sys.exit(1)

updater = UpdateVE(ve_dir=ve_dir)
if updater.virtualenv_needs_update():
    print "VirtualEnv needs to be updated"
    print 'Run deploy/bootstrap.py'
    sys.exit(1)

fab_bin = path.join(ve_dir, 'bin', 'fab')

dye_pkg_dir = find_package_dir_in_ve(ve_dir, 'dye')
if not dye_pkg_dir:
    sys.exit('Could not find fabfile in dye package')
fabfile = path.join(dye_pkg_dir, 'dye', 'fabfile.py')

# tell fabric that this directory is where it can find project_settings and
# localfab (if it exists)
osenv = os.environ
osenv['DEPLOYDIR'] = path.dirname(__file__)

# call the fabric in the virtual env
fab_call = [fab_bin]
# tell it to use the fabfile from dye
fab_call += ['-f', fabfile]

# add any arguments passed to this script
fab_call += sys.argv[1:]

#print "Running fab.py in ve: %s" % ' '.join(fab_call)

# exit with the fabric exit code
sys.exit(subprocess.call(fab_call, env=osenv))
