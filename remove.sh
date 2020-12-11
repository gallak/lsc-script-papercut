#!/bin/bash
SCRIPT_PATH=/srv/lsc-script-papercut
source $SCRIPT_PATH/env/bin/activate
$SCRIPT_PATH/run.py --action delOneUser --user $1
exit $?
