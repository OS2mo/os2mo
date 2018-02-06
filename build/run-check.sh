#!/bin/sh

exec ./manage.py python -- -m flake8 --exit-zero
