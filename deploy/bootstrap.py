#!/usr/bin/env python
# a script to set up the virtualenv so we can use fabric and tasks
import sys
import ve_mgr


def main(argv):
    # check python version is high enough
    ve_mgr.check_python_version(2, 6, __file__)
    updater = ve_mgr.UpdateVE(argv)
    updater.update_git_submodule()
    return updater.update_ve()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
