# functions just for this project
import os
import subprocess
import sys

import tasklib

fixtures_to_load = [
                    'fixtures/publicweb.decision.json',
                    'fixtures/user.json'
                  ]

fixtures_to_deploy = [
                    'fixtures/user.json'
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
        fixtures_list = fixtures_to_deploy
    else:
        fixtures_list = fixtures_to_load
    for fixture in fixtures_list:
        tasklib._manage_py(['loaddata'] + [fixture])