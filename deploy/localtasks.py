# functions just for this project
import os
import subprocess
import sys

import tasklib

production_fixtures = [
                    'initial_data.json.production',
                  ]

development_fixtures = [
                    'initial_data.json.dev',
                     ]
    
def deploy(environment=None, svnuser=None, svnpass=None):
    if environment == None:
        environment = tasklib._infer_environment()

    tasklib.create_ve()
    tasklib.create_private_settings()
    tasklib.link_local_settings(environment)
    tasklib.update_db()
    load_fixtures()

def load_fixtures():
    """load fixtures for this environment"""
    if tasklib._infer_environment() == 'production':
        fixtures_list = production_fixtures
    else:
        fixtures_list = development_fixtures
    for fixture in fixtures_list:
        tasklib._manage_py(['loaddata'] + [fixture])
        
def create_ve():
    """Create the virtualenv"""
    tasklib.create_ve()
    tasklib.patch_south()
    
def update_ve():
    """ Update the virtualenv """
    create_ve()
