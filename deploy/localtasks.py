# functions just for this project
import json
import os
import sys
import subprocess

import tasklib

def post_deploy(environment=None, svnuser=None, svnpass=None):
    load_auth_user(environment)
    load_django_site_data(environment)
        
def load_sample_data(environment, force=False):
    """load sample data if required."""
    if force == False:
        # first check if it has already been loaded
        output_lines = tasklib._manage_py(['dumpdata', 'publicweb'])
        if output_lines[0] != '[]':
            print "Environment '", environment, "' already has sample data loaded."
            return

        tasklib._manage_py(['loaddata', "sample_data.json"])

def _get_objects_from_db(app_name, model_name):
    for output_line in tasklib._manage_py(['dumpdata', "{0}.{1}".format(app_name.lower(), model_name.lower())]):
        try:
            data = json.loads(output_line)
        except ValueError:
            continue
        return data

def _get_matching_objects_from_db(app_name, model_name, target_field_name, target_value):
    data = _get_objects_from_db(app_name, model_name)
    return [object for object in data if object.get(target_field_name) == target_value]

def _auth_user_needs_initializing():
    data = _get_objects_from_db('auth', 'User')
    if not data:
        return True
    elif len(data) == 1 and data[0].get('fields', {}).get('username') == u'AnonymousUser':
        # django-guardian creates User AnonymousUser after syncdb
        return True
    else:
        return False

def load_auth_user(environment, force=False):
    """load auth user fixture based on environment. """
    if force == False:
        if not _auth_user_needs_initializing():
            print "Environment '", environment, "' already has auth.user initialized."
            return

    local_fixtures_directory = os.path.join(tasklib.env['django_dir'], 'publicweb',
                                           'fixtures')
    user_path = os.path.join(local_fixtures_directory,
                                        environment +'_auth_user.json')
    if os.path.exists(user_path):
        tasklib._manage_py(['loaddata', user_path])
    else:
        tasklib._manage_py(['loaddata', "default_auth_user.json"])

def _site_data_needs_initializing():
    # We only care about our app's Site object (ie. the one with id=settings.SITE_ID)
    target_id = 1
    matching_objects = _get_matching_objects_from_db('sites', 'Site', 'pk', target_id)
    if len(matching_objects) > 1:
        raise Exception, "Found more than one Site with id '{0}'".format(target_id)
    if not matching_objects:
        return True
    elif matching_objects[0].get('fields', {}).get('domain', '') == u'example.com':
        # django.contrib.sites automatically creates a Site with domain 
        # 'example.com' when the table is created
        return True
    else:
        return False

def load_django_site_data(environment, force=False):
    """Load data for django sites framework. """
    if force == False:
        if not _site_data_needs_initializing():
            print "Environment '", environment, "' already has site data initialized."
            return
    local_fixtures_directory = os.path.join(tasklib.env['django_dir'], 'publicweb',
                                           'fixtures')
    site_fixture_path = os.path.join(local_fixtures_directory,
                                        environment +'_site.json')
    if os.path.exists(site_fixture_path):
        tasklib._manage_py(['loaddata', site_fixture_path])
    else:
        tasklib._manage_py(['loaddata', "default_site.json"])

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
    cron_grep = tasklib._call_wrapper('sudo crontab -l | grep %s' % tasklib.env['django_dir'], shell=True)
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
    
