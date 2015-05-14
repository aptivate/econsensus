Econsensus
==========

Econsensus is an open source web application tool for consensus decision-making
within one or more organizations, used and written by
[Aptivate](http://aptivate.org).

Send us an email at [volunteering@aptivate.org](mailto:volunteering@aptivate.org)
to let us know you're interested in working on the project, and we'll be 
in touch to see how we can support you.

If you'd like to contribute to this project, please read the rest of this
section, otherwise if you just want to install and try it out, skip to the next
section.

If you'd like to contribute to this project, first of all welcome! Secondly, please follow the workflow below:

- fork the repository on github into your own github account
- follow the instructions below to install a development instance, but instead of cloning from the aptivate repository, clone from the 'develop' branch of your forked repository - always work on the develop branch because that's more up-to-date than master.
- now create a branch of your local develop branch as follows:

```
$ git branch my_branch
```

and check it out:

```
$ git checkout my_branch
```

Please run the tests as you develop, and certainly before submitting your changes to us:

```
$ cd django/econsensus/econsensus
$ rm local_settings.py
$ ln -s local_settings.py.dev_fasttests local_settings.py
$ cd ..
$ ./manage.py test publicweb
```

Once you're done committing and all the tests are passing, push your branch to
your account on github:

```
$ git push origin my_branch
```

* find your branch `my_branch` on your github account and use the github button to submit a pull request to the aptivate develop branch
* we'll get notified of your pull request and will be in touch asap

Thank you for your interest!

Install an instance
===================

This is based on using Ubuntu >= 10.04, but should also work on Debian Squeeze.

First install the requirements:

    $ sudo apt-get install git-core python-virtualenv python-pip sqlite3 \
          python-dev libxml2-dev libyaml-dev mysql-server mysql-client \
          libmysqlclient-dev build-essential libxslt1-dev mercurial

Then check out the code.  For the latest stable code:

    $ git clone https://github.com/aptivate/econsensus.git

For contributors, get the develop branch from your forked repository:

    $ git clone https://github.com/my_user_account/econsensus.git -b develop

Then you should be able to do:

    $ cd econsensus
    $ deploy/bootstrap.py
    $ deploy/tasks.py deploy:dev

This will create the virtualenv and install the python packages required, then
create the database with an initial admin user for use of the django admin
screens and a few other details (see [the dye
readme](https://github.com/aptivate/dye/blob/master/README.md) for more
details). You should now be able to run the development server:

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

We suggest you begin by creating some users and organizations for your new
econsensus instance.  Start by signing up a new member by following the link on
the login screen, log in and then create a new organization for that new
member. Once you've done this, your new member can add other members to their
organization because a creator of a new organization is automatically an admin
level user of that organization. You can also repeat these steps to sign up
more members and create organizations for them, or you can also create new
organizations as an existing logged-in user. 

Installing default help pages
=============================

You can install help pages for the benefit of your users by running

    $ ./manage.py loaddata default_flatpages

The text of these pages can be modified (and pages added or removed)
via the django admin screen. Pages are 'flatpage' instances, and their
content is in [Markdown](http://en.wikipedia.org/wiki/Markdown) format.

Important note on email notifications
=====================================

Please note that the processes described above involve email interaction. An
econsensus instance installed as above is not set up to send out actual emails,
but will instead write emails out as text files into the directory specified by
the `EMAIL_FILE_PATH` setting in `local_settings.py`. This email behaviour is
controlled by the `EMAIL_BACKEND` setting also in `local_settings.py`.

Enabling search
===============

If you are using the dev settings (as set up above) then whoosh is the search
backend used.  See the `HAYSTACK_CONNECTIONS` section of
`econsensus/local_settings.py.dev`

All you need to do to have search actually be able to find the content is to
run:

    ./manage.py update_index

This will create a directory called `whoosh_index` in `django/econsensus/`
that will contain the files required.

Versioning
==========

We've decided to update the version number for every release,  using the following pattern:

v[release number].[major functionality number].[deployment number]

So, v0.4.7 means "Deployment #7, working towards major functionality #5 (which happens to be Action Items), which is part of Release #1"

It's possible that some pieces of major functionality will overtake one-another in terms of completion time - in which case we'll re-number them.

If we get to a double digit, we just roll over, e.g. v0.4.12  .

When we update the version, we also create a bit of documentation on the "updates" flatpage to explain what's new.
