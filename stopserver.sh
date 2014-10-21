#!/bin/bash

if [ ! -f django.pid ]; then
    echo "No PID file found."
    exit 1
fi

kill $(cat django.pid)
rm django.pid
echo "Django has been shut down successfully."
