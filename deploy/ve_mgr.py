import shutil
import sys
import os
import subprocess
from os import path


def find_package_dir_in_ve(ve_dir, package):
    python = os.listdir(path.join(ve_dir, 'lib'))[0]
    site_dir = path.join(ve_dir, 'lib', python, 'site-packages')
    package_dir = path.join(site_dir, package)
    egglink = path.join(site_dir, package + '.egg-link')
    if path.isdir(package_dir):
        return package_dir
    elif path.isfile(egglink):
        return open(egglink, 'r').readline().strip()
    else:
        return None


def find_file(location_list):
    for file_location in location_list:
        if os.path.exists(file_location):
            return file_location
    return None


def find_python():
    """ work out which python to use """
    generic_python = os.path.join('/', 'usr', 'bin', 'python')
    python26 = generic_python + '2.6'
    python27 = generic_python + '2.7'
    paths_to_try = (python27, python26, generic_python, sys.executable)
    python_exe = find_file(paths_to_try)
    if not python_exe:
        raise Exception("Failed to find a valid Python executable " +
                "in any of these locations: %s" % paths_to_try)
    return python_exe


def check_python_version(min_python_major_version, min_python_minor_version, py_path):
    # check python version is high enough
    python_exe = 'python%d.%d' % (min_python_major_version, min_python_minor_version)

    if (sys.version_info[0] < min_python_major_version or
            sys.version_info[1] < min_python_minor_version):
        # we use the environ thing to stop recursing if unexpected things happen
        if 'RECALLED_CORRECT_PYTHON' not in os.environ:
            new_env = os.environ.copy()
            new_env['RECALLED_CORRECT_PYTHON'] = 'true'
            try:
                retcode = subprocess.call([python_exe, py_path] + sys.argv[1:],
                        env=new_env)
                sys.exit(retcode)
            except OSError:
                print >> sys.stderr, \
                    "You must use python %d.%d or later, you are using %d.%d" % (
                        min_python_major_version, min_python_minor_version,
                        sys.version_info[0], sys.version_info[1])
                print >> sys.stderr, "Could not find %s in path" % python_exe
                sys.exit(1)
        else:
            print >> sys.stderr, \
                "You must use python %d.%d or later, you are using %d.%d" % (
                    min_python_major_version, min_python_minor_version,
                    sys.version_info[0], sys.version_info[1])
            print >> sys.stderr, "Try doing '%s %s'" % (python_exe, sys.argv[0])
            sys.exit(1)


def in_virtualenv():
    """ Are we already in a virtualenv """
    return 'VIRTUAL_ENV' in os.environ or 'IN_VIRTUALENV' in os.environ


class UpdateVE(object):

    def __init__(self, ve_root=None, requirements=None):

        if requirements:
            self.requirements = requirements
        else:
            try:
                from project_settings import local_requirements_file
            except ImportError:
                print >> sys.stderr, "could not find local_requirements_file in project_settings.py"
                raise
            self.requirements = local_requirements_file

        if ve_root:
            self.ve_root = ve_root
        else:
            try:
                from project_settings import local_vcs_root, relative_ve_dir
                ve_dir = path.join(local_vcs_root, relative_ve_dir)
            except ImportError:
                print >> sys.stderr, "could not find local_vcs_root/relative_ve_dir in project_settings.py"
                raise
            self.ve_root = ve_dir

        self.ve_timestamp = path.join(self.ve_root, 'timestamp')

    def update_ve_timestamp(self):
        os.utime(self.ve_root, None)
        file(self.ve_timestamp, 'w').close()

    def virtualenv_needs_update(self):
        # timestamp of last modification of .ve/ directory
        ve_dir_mtime = path.exists(self.ve_root) and path.getmtime(self.ve_root) or 0
        # timestamp of last modification of .ve/timestamp file (touched by this
        # script
        ve_timestamp_mtime = path.exists(self.ve_timestamp) and path.getmtime(self.ve_timestamp) or 0
        # timestamp of requirements file (pip_packages.txt)
        reqs_timestamp = path.getmtime(self.requirements)
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

    def update_git_submodule(self):
        """ pip can include directories, and we sometimes add directories as
        submodules.  And pip install will fail if those directories are empty.
        So we need to set up the submodules first. """
        try:
            from project_settings import local_vcs_root, repo_type
        except ImportError:
            print >> sys.stderr, "could not find ve_dir in project_settings.py"
            raise
        if repo_type != 'git':
            return
        subprocess.call(
                ['git', 'submodule', 'update', '--init'],
                cwd=local_vcs_root)

    def update_ve(self, update_ve_quick=False, destroy_old_ve=False, force_update=False):

        if not path.exists(self.requirements):
            print >> sys.stderr, "Could not find requirements: file %s" % self.requirements
            sys.exit(1)

        update_required = self.virtualenv_needs_update()

        if not update_required and not force_update:
            # Nothing to be done
            return False

        # if we need to create the virtualenv, then we must do that from
        # outside the virtualenv. The code inside this if statement will only
        # be run outside the virtualenv.
        if destroy_old_ve and path.exists(self.ve_root):
            shutil.rmtree(self.ve_root)
        if not path.exists(self.ve_root):
            import virtualenv
            virtualenv.logger = virtualenv.Logger(consumers=[])
            virtualenv.create_environment(self.ve_root, site_packages=False)

        # install the pip requirements and exit
        pip_path = path.join(self.ve_root, 'bin', 'pip')
        # use cwd to allow relative path specs in requirements file, e.g. ../tika
        pip_retcode = subprocess.call(
                [pip_path, 'install', '--requirement=%s' % self.requirements],
                cwd=os.path.dirname(self.requirements))
        if pip_retcode == 0:
            self.update_ve_timestamp()
        sys.exit(pip_retcode)
