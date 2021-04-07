#!/usr/bin/env/bash

# This script performs actions that update the website
# This ONLY needs to be run if the github repository changes
# It first sets up environment variables from a .env file
# It then pulls changes off github
# Then, it installs any new packages
# Next, it updates static files (CSS/JS) and the database
# Finally, it reloads the webapp

echo Installing any new packages
pip3 install -r requirements.txt
echo Updating Database
python manage.py migrate
