#!/usr/bin/env python3
# https://pypi.org/project/randomuser/

import pprint
import configparser
import logging
import sys
from argparse import ArgumentParser
from lib import papercut



# import de la configuration
confParser = configparser.ConfigParser()
confParser.optionxform = lambda option: option
confParser.read("/srv/lsc-script-papercut/papercut.cfg")

# creation du logger
logger = logging.getLogger("pcLog")
# format de log
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# niveau de log
#loglevel=confParser["log"].get("loglevel")
logger.setLevel(logging.DEBUG)
# handler
fh = logging.FileHandler(confParser["log"].get("logfile"))
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
  pcCnx.url=confParser["server"].get("url")
  pcCnx.token=confParser["server"].get("token")
  pcCnx.mapping=dict(confParser["lsc-mapping"])
  pcCnx.pivot=confParser["lsc-pivot"].get("pivot")
#  pcCnx.logger = logger
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
     pcCnx.addPapercutLscExec(sys.stdin)
    else :
     logger.debug("%s is not a valid action see --help options")
     exit(255)
