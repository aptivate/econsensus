Econsensus
==========

Econsensus is an open source web application tool for consensus decision-making within one or more organizations, 
used and written by [Aptivate](http://aptivate.org).

Documentation and assistance
============================

Please read the [documentation](http://old.aptivate.org/econsensus) and feel free to join the 
[discussion](https://groups.google.com/forum/?fromgroups#!forum/econsensusdiscuss).

Install a development instance
==============================

This is based on using Ubuntu >= 10.04, but should also work on Debian Squeeze.

First install the requirements:

    $ sudo apt-get install git-core python-virtualenv python-pip sqlite3 \
          python-dev libxml2-dev libyaml-dev mysql-server mysql-client \
          libmysqlclient-dev build-essential libxslt1-dev mercurial

Then check out the code:

    $ git clone https://github.com/aptivate/econsensus.git

Then you should be able to do:

    $ cd econsensus
    $ deploy/tasks.py deploy:dev

This should set up the database you need, install the python packages 
required, create an initial admin user for use of the django admin screens 
and a few other details. You should now be able to run the 
development server:

    $ cd django/econsensus/
    $ ./manage.py runserver
    
Use the development instance
============================

You should now be able to access the django admin screens at:

    http://127.0.0.1:8000/admin/

using the admin user with username and password 'admin'. This password can be changed 
via the django admin screens (see User table).

You should also be able to access the application screens at:

    http://127.0.0.1:8000/
    
which will show you the login screen, or allow you to "Sign up as a new member". 

We suggest you begin by creating some users and organizations for your new econsensus instance.
Start by signing up a new member by following the link on the login screen, log in and 
then create a new organization for that new member. Once you've done this, your new member can 
add other members to their organization because a creator of a new organization is automatically 
an admin level user of that organization. You can also repeat
these steps to sign up more members and create organizations for them, or you can also create new 
organizations as an existing logged-in user. 

Important note on email notifications
-------------------------------------
Please note that the processes described above involve email interaction. An econsensus instance installed as above is not set up to send out 
actual emails, but will instead write emails out as text files into the directory specified by the 
EMAIL_FILE_PATH setting in local_settings.py. This email behaviour is controlled by the EMAIL_BACKEND 
setting also in local_settings.py.



                                                                                                                                                                                                                                                                                            
