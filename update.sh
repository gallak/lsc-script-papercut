#!/bin/bash
cat - >> /tmp/update.log
source $LSC_PC_BIN_PATH/env/bin/activate
$LSC_PC_BIN_PATH/run.py --action updateOneUser --user $1
exit $?
