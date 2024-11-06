#!/bin/bash
set -e
cd cough_classification
python manage.py migrate
python manage.py makesuperuser
