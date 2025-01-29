#!/bin/bash
set -e
gunicorn cough_classification.wsgi --log-file -
