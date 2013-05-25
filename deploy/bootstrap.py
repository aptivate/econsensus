#!/usr/bin/env python
# a script to set up the virtualenv so we can use fabric and tasks

import os
import sys
import getopt
import ve_mgr

# check python version is high enough
MIN_PYTHON_MAJOR_VERSION = 2
MIN_PYTHON_MINOR_VERSION = 6
update_ve.check_python_version(
    MIN_PYTHON_MAJOR_VERSION, MIN_PYTHON_MINOR_VERSION, __file__)

DEPLOY_DIR = os.path.abspath(os.path.dirname(__file__))
REQUIREMENTS = os.path.join(DEPLOY_DIR, 'bootstrap_requirements.txt')


def main(argv):
    verbose = False
    try:
        opts, args = getopt.getopt(argv[1:], 'hqv',
                ['help', 'quiet', 'verbose'])
    except getopt.error, msg:
        print 'Bad options: %s' % msg
        return 1
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            pass
            #print_help_text()
        if o in ("-v", "--verbose"):
            verbose = True

    current_dir = os.path.dirname(__file__)
    ve_dir = os.path.join(current_dir, '.ve.deploy')

    updater = ve_mgr.UpdateVE(ve_dir, REQUIREMENTS)
    updater.update_ve()

    # TODO: could now print instructions for local deploy and fab deploy ...
    if verbose:
        print "Now you can run tasks.py or fab.py"

if __name__ == '__main__':
    sys.exit(main(sys.argv))
