#!/usr/bin/env python
# a script to set up the virtualenv so we can use fabric and tasks
import sys
import getopt
import ve_mgr

# check python version is high enough
ve_mgr.check_python_version(2, 6, __file__)


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

    updater = ve_mgr.UpdateVE()
    updater.update_ve()

    # TODO: could now print instructions for local deploy and fab deploy ...
    if verbose:
        print "Now you can run tasks.py or fab.py"

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
