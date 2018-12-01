#!/bin/bash
backend_dir='/usr/local/seevenv/see-master/backend/' 
frontend_dir='/usr/local/seevenv/see-master/frontend/'
\cp -r ../backend/* $backend_dir
\cp -r ../frontend/* $frontend_dir
cd $backend_dir
source ../../bin/activate
python manage.py makemigrations
python manage.py migrate

