#!/bin/bash
source $LSC_PC_BIN_PATH/env/bin/activate
#echo "phase de list" >> /tmp/action
$LSC_PC_BIN_PATH/run.py
exit $?
