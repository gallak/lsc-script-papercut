#!/usr/bin/env python3
# https://pypi.org/project/randomuser/

import pprint
import configparser
import logging
from argparse import ArgumentParser
from lib import papercut



# import de la configuration
confParser = configparser.Config()
confParser.read("papercut.cfg")

# creation du logger
logger = logging.getLogger("pcLog")
# format de log
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# niveau de log
logger.setLevel(logging.parser["log"].get("loglevel"))
# handler
fh = logging.FileHandler(logging.parser["log"].get("logfile")
fh.setLevel(logging.parser["log"].get("loglevel"))
fh.setFormatter(formatter)
logger.addHandler(fh)

# option from commandline

cliParser=argparse.ArgumentParser( prog = 'run', description =""" Script used to sync PAPERCUT """)

cliParser.add_argument("--getListUsers", help="List all account from PAPERCUT server")
cliParser.add_argument("--getOneUser", help="Fetch one user's attributes from PAPERCUT server", type =str)
cliParser.add_argument("--updateOneUser", help="Update one user's attributes from PAPERCUT server with LDIF from stdin", type =str)
cliParser.add_argument("--delOneUser", help="delete one user from PAPERCUT server", type =str)
cliParser.add_argument("--dumpAllUsers", help="dump all attributs from all user from PAPERCUT server")


PcAttributs=['username','username-alias','full-name','email','primary-card-number','secondary-card-number','office','card-pin','department']


if __name__ == '__main__':
  pcCnx=papercut.PaperCut()
  pcCnx.url=confParser["server"].get("url")
  pcCnx.token=confParser["server"].get("token")
  pcCnx.mapping=confParser["mapping"]

  pcCnx.connect()

  arguments = cliParser.parse_args()
  if arguments.getListUsers:
    pprint.pprint(pcCnx.list_users())

  if arguments.getOneUSer:
    pcCnx.getPapercutLscExec(arguments.getOneUSer,PcAttributs)

  if arguments.updateOneUser:
    pcCnx.updatePapercutLscExec(arguments.updateOneUser,sys.stdin)

  if arguments.delOneUser:
    pcCnx.removePapercutLscExec(arguments.delOneUser)

  if arguments.dumpAllUsers:
    pcCnx.show_all_user_details(PcAttributs)
