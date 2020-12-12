#!/bin/bash
source $LSC_PC_BIN_PATH/env/bin/activate
$LSC_PC_BIN_PATH/run.py --action createOneUser --user $1
exit $?
