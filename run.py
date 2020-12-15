#!/usr/bin/env python3
# https://pypi.org/project/randomuser/

import pprint
import logging
import sys
import os
from argparse import ArgumentParser
from lib import papercut




# creation du logger
logger = logging.getLogger("pcLog")
# format de log
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# niveau de log
#loglevel=confParser["log"].get("loglevel")
logger.setLevel(logging.DEBUG)
# handler
debugfile=os.environ.get("LSC_PC_LOG_FILE")
fh = logging.FileHandler(debugfile)
#fh.setLevel(logging.confParser["log"].get("loglevel"))
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)
#ch = logging.StreamHandler()
#logger.addHandler(ch)

# option from commandline

cliParser=ArgumentParser( prog = 'run', description =""" Script used to sync PAPERCUT with LSC trough lsc plugin exec""")
cliParser.add_argument("--action", help="one of the following action : getAllUser / getOneUser (need username) / createOneUser (need username and ldif) / updateOneUser (need username and ldif from stdin) / delOneUser (need username) / dumpAllUser")
cliParser.add_argument("--user", help="username to use for get/updateOne/delete user from PAPERCUT server", type =str)


if __name__ == '__main__':
  pcCnx=papercut.PaperCut()
  # Init Class witch value
  pcCnx.url=os.environ.get("LSC_PC_URL")
  pcCnx.token=os.environ.get("LSC_PC_TOKEN")
  pcCnx.pivot=os.environ.get("LSC_PC_PIVOT")
  pcCnx.papercutAttributs=os.environ.get("LSC_PC_ATTRIBUTS").split(",")
  pcCnx.connect()

  arguments = cliParser.parse_args()
  if arguments.action:
    logger.debug(" Action %s called", arguments.action)
    if arguments.action == "getAllUser" :
      pcCnx.listPapercutLscExec()
    elif arguments.action == "getOneUser" :
      pcCnx.getPapercutLscExec(arguments.user,sys.stdin)
    elif arguments.action == "updateOneUser" :
      pcCnx.updatePapercutLscExec(arguments.user,sys.stdin)
    elif arguments.action == "delOneUser" :
      pcCnx.removePapercutLscExec(arguments.user)
    elif arguments.action == "dumpAllUser" :
      pcCnx.show_all_user_details(PcAttributs)
    elif arguments.action == "createOneUser" :
     pcCnx.addPapercutLscExec(arguments.user,sys.stdin)
    else :
     logger.debug("%s is not a valid action see --help options")
     exit(255)
