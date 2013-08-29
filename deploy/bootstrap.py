#!/usr/bin/env python
"""
bootstrap.py will set up a virtualenv for you and update it as required.

Usage:
    bootstrap.py               # update virtualenv
    bootstrap.py fake          # just update the virtualenv timestamps
    bootstrap.py clean         # delete the virtualenv
    bootstrap.py -h | --help   # print this message and exit

Options for the plain command:
    -f, --force            # do the virtualenv update even if it is up to date
    -r, --full-rebuild     # delete the virtualenv before rebuilding
    -q, --quiet            # don't ask for user input
"""
# a script to set up the virtualenv so we can use fabric and tasks
import sys
import getopt
import ve_mgr


def print_help_text():
    print __doc__


def print_error_msg(error_msg):
    print error_msg
    print_help_text()
    return 2


def main(argv):
    # check python version is high enough
    ve_mgr.check_python_version(2, 6, __file__)

    force_update = False
    full_rebuild = False
    fake_update = False
    clean_ve = False

    if argv:
        try:
            opts, args = getopt.getopt(argv[1:], 'hfqr',
                ['help', 'force', 'quiet', 'full-rebuild'])
        except getopt.error, msg:
            return print_error_msg('Bad options: %s' % msg)
        # process options
        for o, a in opts:
            if o in ("-h", "--help"):
                print_help_text()
                return 0
            if o in ("-f", "--force"):
                force_update = True
            if o in ("-r", "--full-rebuild"):
                full_rebuild = True
        if len(args) > 1:
            return print_error_msg(
                    "Can only have one argument - you had %s" % (' '.join(args)))
        if len(args) == 1:
            if args[0] == 'fake':
                fake_update = True
            elif args[0] == 'clean':
                clean_ve = True

        # check for incompatible flags
        if force_update and fake_update:
            return print_error_msg("Cannot use --force with fake")
        if full_rebuild and fake_update:
            return print_error_msg("Cannot use --full-rebuild with fake")
        if full_rebuild and clean_ve:
            return print_error_msg("Cannot use --full-rebuild with clean")

    updater = ve_mgr.UpdateVE()
    if fake_update:
        return updater.update_ve_timestamp()
    elif clean_ve:
        return updater.delete_virtualenv()
    else:
        updater.update_git_submodule()
        return updater.update_ve(full_rebuild, force_update)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
