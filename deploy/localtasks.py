# functions just for this project
import os, sys
import subprocess

import tasklib

def deploy(environment=None, svnuser=None, svnpass=None):
    if environment == None:
        environment = tasklib._infer_environment()

    tasklib.create_ve()
    tasklib.create_private_settings()
    tasklib.link_local_settings(environment)
    tasklib.update_db()

    load_admin_user(environment)
    load_django_site_data(environment)
        
def load_sample_data(environment, force=False):
    """load sample data if required."""
    if force == False:
        # first check if it has already been loaded
        output_lines = tasklib._manage_py(['dumpdata', 'publicweb'], supress_output=True)
        if output_lines[0] != '[]':
            print "Environment '", environment, "' already has sample data loaded."
            return

        tasklib._manage_py(['loaddata', "sample_data.json"])

def load_admin_user(environment):
    """load admin user based on environment. """
    # TODO: maybe check if the admin user already exists before replacing it ...
    local_fixtures_directory = os.path.join(tasklib.env['django_dir'], 'publicweb',
                                           'fixtures')
    admin_user_path = os.path.join(local_fixtures_directory,
                                        environment +'_admin_user.json')
    if os.path.exists(admin_user_path):
        tasklib._manage_py(['loaddata', admin_user_path])
    else:
        tasklib._manage_py(['loaddata', "default_admin_user.json"])

def load_django_site_data(environment, force=False):
    """load data for django sites framework. """
    if force == False:
        # first check if it has already been loaded
        output_lines = tasklib._manage_py(['dumpdata', 'sites'], supress_output=True)
        if output_lines[0] != '[]':
            print "Environment '", environment, "' already has site data loaded."
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
    # */5 * * * * /usr/bin/python26 /var/django/openconsent/dev/django/openconsent/manage.py process_email
    f = open(cron_file, 'w')
    try:
        f.write('*/5 * * * * root /usr/bin/python26 %s/manage.py process_email' % tasklib.env['django_dir'])
        f.write('\n')
    finally:
        f.close()
    
    os.chmod(cron_file, 0755)
    