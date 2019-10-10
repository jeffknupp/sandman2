#!/bin/sh

# Start sandman2

if [ $DB_TYPE == "sqlite" ] then
    sandman2ctl -p $PORT $DB_TYPE+$DB_DRIVER:///$DATABASE
else
    sandman2ctl -p $PORT $DB_TYPE+$DB_DRIVER://$USERNAME:$PASSWORD@$DB_NAME:$DB_PORT/$DATABASE
fi
