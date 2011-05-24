import os, sys

project_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(project_dir, '../django')))
sys.path.append(os.path.abspath(os.path.join(project_dir, '/django/openconsent/')))

#print >> sys.stderr, sys.path

#sys.path.append('/var/project_name-stage')

os.environ['DJANGO_SETTINGS_MODULE'] = 'openconsent.settings'
os.environ['OPENCONSENT_HOME'] = '/var/django/openconsent/dev/django/'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

