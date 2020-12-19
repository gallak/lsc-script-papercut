#!/bin/bash
source $LSC_PC_BIN_PATH/bin/activate
#echo "phase de list" >> /tmp/action
$LSC_PC_BIN_PATH/run.py
exit $?
