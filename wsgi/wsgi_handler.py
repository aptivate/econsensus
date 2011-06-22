import os, sys, site

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')

# ensure the virtualenv for this instance is added
site.addsitedir(os.path.join(project_dir, 'django', 'openconsent', '.ve', 
                              'lib', 'python2.6', 'site-packages'))
# not sure about this - might be required for packages installed from
# git/svn etc
#site.addsitedir(os.path.join(project_dir, 'django', 'openconsent', '.ve', 'src'))

sys.path.append(os.path.join(project_dir, 'django'))
sys.path.append(os.path.join(project_dir, 'django', 'openconsent'))

#print >> sys.stderr, sys.path

#sys.path.append('/var/project_name-stage')

os.environ['DJANGO_SETTINGS_MODULE'] = 'openconsent.settings'
os.environ['OPENCONSENT_HOME'] = '/var/django/openconsent/dev/django/'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

