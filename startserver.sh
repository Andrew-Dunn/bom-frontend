#!/bin/bash

function int-ip { /sbin/ifconfig $1 | grep "inet addr" | awk -F: '{print $2}' | awk '{print $1}'; }

source env/bin/activate
nohup python manage.py runserver $(int-ip eth0):8080 &
deactivate
