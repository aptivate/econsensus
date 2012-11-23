# this is for settings to be used by tasks.py

###############################
# THESE SETTINGS MUST BE EDITED
###############################

# This is the directory inside the project dev dir that contains the django
# application
project_name = "econsensus"

# The django apps that are part of this project - used for running tests
# and migrations
django_apps  = ['publicweb', ]

# repository type can be "cvs", "svn" or "git"
repo_type = "git"
repository = 'git://github.com/aptivate/openconsent.git'

##################################################################
# THESE SETTINGS MAY WELL BE CORRECT FOR A STANDARD DJANGO PROJECT
# BUT SHOULD STILL BE REVIEWED
##################################################################

# put "django" here if you want django specific stuff to run
# put "plain" here for a basic apache app
project_type = "django"

# does this virtualenv for python packages
use_virtualenv = True

# the path from the project root to the django root dir
django_relative_dir   = "django/" + project_name

test_cmd = ' manage.py test -v0 ' + ' '.join(django_apps)


# servers, for use by fabric

# production server - if commented out then the production task will abort
host_list = {
        'production':   ['lin-' + project_name + '.aptivate.org:48001',],
        'staging':      ['fen-vz-' + project_name + '.fen.aptivate.org',],
        'staging_test': ['fen-vz-' + project_name + '.fen.aptivate.org',],
        #'dev_server':   ['fen-vz-' + project_name + '-dev.fen.aptivate.org',],
        }

# where on the server the django apps are deployed
server_home = '/var/django'

# the top level directory on the server
project_dir = project_name

# which web server to use (or None)
webserver = 'apache'

###################################################
# OPTIONAL SETTINGS FOR FABRIC - will be put in env
###################################################

# if you have an ssh key and particular user you need to use
# then uncomment the next 2 lines
#user = "root"
#key_filename = ["/home/shared/keypair.rsa"]
