# functions just for this project
import os

from dye import tasklib
from dye.tasklib.django import _manage_py
from dye.tasklib.util import _call_wrapper


def post_deploy(environment=None, svnuser=None, svnpass=None):
    load_auth_user(environment)
    load_django_site_data(environment)


def load_sample_data(environment, force=False):
    """load sample data if required."""
    if force is False:
        # first check if it has already been loaded
        output_lines = _manage_py(['dumpdata', 'publicweb'])
        if output_lines[0] != '[]':
            print "Environment '", environment, "' already has sample data loaded."
            return

        _manage_py(['loaddata', "sample_data.json"])


def load_auth_user(environment, force=False):
    """load auth user fixture based on environment. """
    if force is False:
        auth_user_needs_initializing = int(_manage_py(['auth_user_needs_initializing'])[0].strip())
        if not auth_user_needs_initializing:
            print "Environment '", environment, "' already has auth.user initialized."
            return

    local_fixtures_directory = os.path.join(tasklib.env['django_dir'], 'publicweb',
                                           'fixtures')
    user_path = os.path.join(local_fixtures_directory,
        environment + '_auth_user.json')
    if os.path.exists(user_path):
        _manage_py(['loaddata', user_path])
    else:
        _manage_py(['loaddata', "default_auth_user.json"])


def load_django_site_data(environment, force=False):
    """Load data for django sites framework. """
    if force is False:
        site_needs_initializing = int(_manage_py(['site_needs_initializing'])[0].strip())
        if not site_needs_initializing:
            print "Environment '", environment, "' already has site data initialized."
            return
    local_fixtures_directory = os.path.join(tasklib.env['django_dir'], 'publicweb',
                                           'fixtures')
    site_fixture_path = os.path.join(local_fixtures_directory,
        environment + '_site.json')
    if os.path.exists(site_fixture_path):
        _manage_py(['loaddata', site_fixture_path])
    else:
        _manage_py(['loaddata', "default_site.json"])


def create_ve():
    """Create the virtualenv"""
    tasklib.create_ve()
    tasklib.patch_south()


def update_ve():
    """ Update the virtualenv """
    create_ve()


def add_cron_email(environment):
    """sets up a cron job for the email checking"""

    cron_file = os.path.join('/etc', 'cron.d', 'cron_email_%s' % environment)
    if os.path.exists(cron_file):
        return
    # has it been set up already?
    cron_grep = _call_wrapper('sudo crontab -l | grep %s' % tasklib.env['django_dir'], shell=True)
    if cron_grep == 0:
        return

    # write something like:
    # */5 * * * * /usr/bin/python26 /var/django/econsensus/dev/django/econsensus/manage.py process_email
    f = open(cron_file, 'w')
    try:
        f.write('*/5 * * * * apache /usr/bin/python26 %s/manage.py process_email' % tasklib.env['django_dir'])
        f.write('\n')
    finally:
        f.close()

    os.chmod(cron_file, 0644)
