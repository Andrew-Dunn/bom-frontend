#!/bin/bash

function int-ip { /sbin/ifconfig $1 | grep "inet addr" | awk -F: '{print $2}' | awk '{print $1}'; }

source env/bin/activate
nohup python manage.py runserver $(int-ip eth0):8080 &

sleep 5s

PARENT_PID=$!
DJANGO_PID=$(ps ax | grep "runserver $(int-ip eth0):8080" | grep -v grep | grep -v "$PARENT_PID" | awk '{ print $1 }')
echo $DJANGO_PID > django.pid

deactivate
