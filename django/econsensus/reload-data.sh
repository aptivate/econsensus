#!/bin/sh
rm econsensus.sqlite
./manage.py syncdb --migrate
./manage.py loaddata publicweb/fixtures/users.json 
./manage.py loaddata publicweb/fixtures/organizations.json 
./manage.py loaddata publicweb/fixtures/decisions.json 

