#!/bin/bash

if [ "$1" == "" ] || [ $# -gt 1 ]; then
    echo PORT is not specified;
    exit 1
fi

PORT=$1

#gunicorn app:server -b :$PORT
gunicorn app:server --reload -b :$PORT
