#!/bin/bash
set -e

DEBUG=${DEBUG}
ENVIRONMENT=${ENVIRONMENT}
HOST=${HOST}
PORT=${PORT}

if [ "${ENVIRONMENT}" == "development" ]; then
    echo "Running in development mode"
    exec flask run --host=${HOST} --port=${PORT} --debug --reload
else
    echo "The only supported environment is development."
    exit 1
fi
