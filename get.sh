#!/bin/bash
source $LSC_PC_BIN_PATH/env/bin/activate
$LSC_PC_BIN_PATH/run.py --user $1

exit $?
