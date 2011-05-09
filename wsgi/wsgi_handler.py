import os, sys

project_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(project_dir, '..')))
sys.path.append(os.path.abspath(os.path.join(project_dir, '../project_name/')))

#print >> sys.stderr, sys.path

#sys.path.append('/var/project_name-stage')

os.environ['DJANGO_SETTINGS_MODULE'] = 'project_name.settings'
os.environ['PROJECT_NAME_HOME'] = '/var/django/project_name/dev/'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

