# functions just for this project
import os

from dye import tasklib
from dye.tasklib.django import _manage_py
from dye.tasklib.util import _call_wrapper


def post_deploy(environment=None, svnuser=None, svnpass=None):
    load_auth_user(environment)
    load_django_site_data(environment)
    load_required_flat_pages(environment)
    load_waffles(environment)
    update_search_index()


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
    _conditionally_load_data(environment, force, 'auth.user',
                             'auth_user_needs_initializing', '_auth_user')


def load_django_site_data(environment, force=False):
    """Load data for django sites framework. """
    _conditionally_load_data(environment, force, 'site date',
                             'site_needs_initializing', '_site')


def load_required_flat_pages(environment, force=False):
    """ The templates assume that the about and help flatpages exists and
    are likely to explode without them.  So if they don't exist, load a
    fixture to create them. """
    _conditionally_load_data(environment, force, 'flat pages',
                             'flatpages_needs_initializing', '_flatpages')


def load_waffles(environment, force=False):
    """load waffle fixture based on environment. """
    _conditionally_load_data(environment, force, 'waffles',
                             'waffles_need_initializing', '_waffles')


def _conditionally_load_data(environment, force, name, manage_cmd, fixture_suffix):
    if force is False:
        needs_initializing = int(_manage_py([manage_cmd])[0].strip())
        if not needs_initializing:
            print "Environment '", environment, "' already has ", name, " initialized."
            return
    local_fixtures_directory = os.path.join(
        tasklib.env['django_dir'], 'publicweb', 'fixtures')
    fixture_path = os.path.join(
        local_fixtures_directory, environment + fixture_suffix + '.json')
    if os.path.exists(fixture_path):
        _manage_py(['loaddata', fixture_path])
    else:
        _manage_py(['loaddata', "default" + fixture_suffix + ".json"])


def update_search_index():
    _manage_py(['update_index'])


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
