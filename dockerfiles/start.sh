#!/bin/sh

# Start flask_sandman

if [ $DB_TYPE == "sqlite" ]; then
    sandman2ctl $DB_TYPE+$DB_DRIVER:////$DATABASE
else
    sandman2ctl $DB_TYPE+$DB_DRIVER://$USERNAME:$PASSWORD@$DB_HOST:$DB_PORT/$DATABASE
fi
