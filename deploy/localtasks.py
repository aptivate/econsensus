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
    link_local_fixtures(environment)
    tasklib.update_db()
    load_fixtures()

def link_local_fixtures(environment):
    """ link local_settings.py.environment as local_settings.py """
    # die if the correct local settings does not exist
    local_fixtures_directory = os.path.join(tasklib.env['django_dir'], 'publicweb',
                                           'fixtures')
    local_fixtures_path = os.path.join(local_fixtures_directory,
                                        'initial_data.json.'+environment)
    if not os.path.exists(local_fixtures_path):
        print "Could not find file to link to: %s" % local_fixtures_path
        sys.exit(1)
    for fixture in fixtures_to_deploy:
        # eg. 'ln -s initial_data.json.dev initial_data.json
        subprocess.call(['ln', '-s', fixture+'.'+environment, fixture], 
                cwd=local_fixtures_directory)

def load_fixtures():
    """load fixtures for this environment"""
    for fixture in fixtures_to_deploy:
        tasklib._manage_py(['loaddata'] + [fixture])
        
def create_ve():
    """Create the virtualenv"""
    tasklib.create_ve()
    tasklib.patch_south()
    
def update_ve():
    """ Update the virtualenv """
    create_ve()
