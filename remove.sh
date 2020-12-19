#!/bin/bash
source $LSC_PC_BIN_PATH/env/bin/activate
echo "phase de clean de $1" >> /tmp/action
$LSC_PC_BIN_PATH/run.py --user $1
exit $?
