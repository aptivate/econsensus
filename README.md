Econsensus
==========

Econsensus is an open source web application tool for consensus decision-making within one or more organizations, 
used and written by [Aptivate](http://aptivate.org).

Please read the [documentation](http://old.aptivate.org/econsensus) and feel free to join the 
[discussion](https://groups.google.com/forum/?fromgroups#!forum/econsensusdiscuss).

If you'd like to contribute to this project, please read the rest of this section, otherwise 
if you just want to install and try it out, skip to the next section.

If you'd like to contribute to this project, first of all welcome! Secondly, please follow the workflow below:
- fork the repository on github into your own github account
- follow the instructions below to install a development instance, but instead of cloning from the aptivate repository, clone from the 'develop' branch of your forked repository - always work on the develop branch because 
that's more up-to-date than master.
- now create a branch of your local develop branch as follows:
 
    $ git branch my\_branch

- and check it out:

    $ git checkout my\_branch
    
- please run the tests as you develop, and certainly before submitting your changes to us:

    $ cd django/econsensus
    
    $ rm local\_settings.py
    
    $ ln -s local\_settings.py.dev\_fasttests local\_settings.py
    
    $ ./manage.py test publicweb
    
- once you're done committing and all the tests are passing, push your branch to your account on github:

    $ git push origin my\_branch
    
- find your branch my\_branch on your github account and use the github button to submit a pull request to the aptivate 
develop branch
- we'll get notified of your pull request and will be in touch asap

Thank you for your interest!

Install an instance
===================

This is based on using Ubuntu >= 10.04, but should also work on Debian Squeeze.

First install the requirements:

    $ sudo apt-get install git-core python-virtualenv python-pip sqlite3 \
          python-dev libxml2-dev libyaml-dev mysql-server mysql-client \
          libmysqlclient-dev build-essential libxslt1-dev mercurial

Then check out the code:

    $ # for the latest stable code:
    $ git clone https://github.com/aptivate/econsensus.git
    $ # for contributors, get the develop branch from your forked repository:
    $ git clone https://github.com/my\_user\_account/econsensus.git -b develop

Then you should be able to do:

    $ cd econsensus
    $ deploy/bootstrap.py
    $ deploy/tasks.py deploy:dev

This will create the virtualenv and install the python packages required, then 
create the database with an initial admin user for use of the django admin screens 
and a few other details (see https://github.com/aptivate/dye/blob/master/README.md for 
more details). You should now be able to run the development server:

    $ cd django/econsensus/
    $ ./manage.py runserver
    
Use the instance
================

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

Installing default help pages
=============================

You can install help pages for the benefit of your users by running

    $ ./manage.py loaddata default\_flatpages

The text of these pages can be modified (and pages added or removed)
via the django admin screen. Pages are 'flatpage' instances, and their
content is in [Markdown](http://en.wikipedia.org/wiki/Markdown) format.

Important note on email notifications
-------------------------------------
Please note that the processes described above involve email interaction. An econsensus instance installed as above is not set up to send out 
actual emails, but will instead write emails out as text files into the directory specified by the 
EMAIL\_FILE\_PATH setting in local\_settings.py. This email behaviour is controlled by the EMAIL\_BACKEND 
setting also in local\_settings.py.



                                                                                                                                                                                                                                                                                            
