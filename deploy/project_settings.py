# this is for settings to be used by tasks.py

# This is the directory inside the project dev dir that contains the django
# application
project_name = 'openconsent'

# put "django" here if you want django specific stuff to run
# put "plain" here for a basic apache app
project_type = "django"

django_dir = "django/" + project_name

django_apps = ['publicweb', ]
