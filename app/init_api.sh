#!/bin/bash
if [ $ENVIRONMENT == 'dev' ] ; then 
    bash /start-reload.sh
else 
    bash /start.sh
fi
