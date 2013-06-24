import os, sys, site

vcs_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# ensure the virtualenv for this instance is added
site.addsitedir(os.path.join(vcs_root_dir, 'django', 'econsensus', '.ve',
                             'lib', 'python2.6', 'site-packages'))

sys.path.append(os.path.join(vcs_root_dir, 'django', 'econsensus'))

#print >> sys.stderr, sys.path

os.environ['DJANGO_SETTINGS_MODULE'] = 'econsensus.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
