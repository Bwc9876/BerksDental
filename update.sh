#!/usr/bin/env bash

# This script performs actions that update the website
# This ONLY needs to be run if the github repository changes
# It first sets up environment variables from a .env file
# It then pulls changes off github
# Then, it installs any new packages
# Next, it updates static files (CSS/JS) and the database
# Finally, it reloads the webapp

# shellcheck disable=SC2034
WSGI_FILE=/var/www/name_of_webapp_wsgi.py

echo Starting Up
set -a; source .env; set +a
echo Checking For/Downloading Changes Off GitHub
git pull
echo Installing any new packages
pip3 install -r requirements.txt
echo Updating Static Files
python manage.py collectstatic --noinput
echo Updating Database
python manage.py makemigrations
python manage.py migrate
echo Reloading Webapp
touch WSGI_FILE
echo Update Complete, please wait a bit for the webapp to reload