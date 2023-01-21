#! /bin/bash
gunicorn -w 4 'listen:app' -b 0.0.0.0 --access-logfile -
