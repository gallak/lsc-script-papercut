#!/usr/bin/env python3
# https://pypi.org/project/randomuser/

import pprint
import configparser
import logging
from argparse import ArgumentParser
from lib import papercut



# import de la configuration
confParser = configparser.ConfigParser()
confParser.read("papercut.cfg")

# creation du logger
logger = logging.getLogger("pcLog")
# format de log
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# niveau de log
#pprint.pprint(confParser["log"].get("loglevel"))
logger.setLevel(logging.DEBUG)
# handler
fh = logging.FileHandler(confParser["log"].get("logfile"))
#fh.setLevel(logging.confParser["log"].get("loglevel"))
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

# option from commandline

cliParser=ArgumentParser( prog = 'run', description =""" Script used to sync PAPERCUT """)

cliParser.add_argument("--action", help="one of the following action : getAllUser / getOneUser (need username) / updateOneUser (need username and ldif from stdin) / delOneUser (need username) / dumpAllUser")
cliParser.add_argument("--user", help="username to use for get/updateOne/delete user from PAPERCUT server", type =str)


PcAttributs=['username','username-alias','full-name','email','primary-card-number','secondary-card-number','office','card-pin','department']


if __name__ == '__main__':
  pcCnx=papercut.PaperCut()
  pcCnx.url=confParser["server"].get("url")
  pcCnx.token=confParser["server"].get("token")
  pcCnx.mapping=confParser["mapping"]

  pcCnx.connect()

  arguments = cliParser.parse_args()
  if arguments.action:
    if arguments.action == "getAllUser" :
      pprint.pprint(pcCnx.list_users())
    elif arguments.action == "getOneUser" :
      pcCnx.getPapercutLscExec(arguments.user,PcAttributs)
    elif arguments.action == "updateOneUser" :
      pcCnx.updatePapercutLscExec(arguments.user,sys.stdin)
    elif rguments.action == "delOneUser" :
      pcCnx.removePapercutLscExec(arguments.user)
    elif rguments.action == "dumpAllUser" :
      pcCnx.show_all_user_details(PcAttributs)
