#!/usr/bin/env python3
# https://pypi.org/project/randomuser/

import pprint
import logging
import sys
import os
from argparse import ArgumentParser
from lib import papercut
import ldif




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
cliParser.add_argument("--user", help="username to use for get/updateOne/delete user from PAPERCUT server", type =str)


def convertLdapRecord(ldapRecord):
  # clean LDAP phase
  for item in ["-","changetype","username","dn","replace","add"]:
    try:
      del ldapRecord[item]
    except KeyError as x:
      logger.debug("No %s element to clean",item)
  # correct Phase
  data=[]
  for key, value in ldapRecord.items():
    val=[key,value[0].decode()]
    FIXME: faire la conversion de TAG
    data.append(val)
  return(data)


if __name__ == '__main__':
  pcCnx=papercut.PaperCut()
  # Init Class witch value
  pcCnx.url=os.environ.get("LSC_PC_URL")
  
  pcCnx.token=os.environ.get("LSC_PC_TOKEN")
  pcCnx.pivot=os.environ.get("LSC_PC_PIVOT")
  pcCnx.papercutAttributs=os.environ.get("LSC_PC_ATTRIBUTS").split(",")
  pcCnx.connect()

  pivot=os.environ.get("LSC_PC_PIVOT")

  arguments = cliParser.parse_args()

  if sys.stdin.isatty() :
    print("pas d'input  c'est une liste")
    #pcCnx.listPapercutLscExec()
  else:
    try : 
      inputData = ldif.LDIFRecordList(sys.stdin)
      inputData.parse()
      ldapRecord = inputData.all_records[0][1]
      try : 
        ldapAction = ldapRecord['changetype'][0].decode()
      except Exception as e:
        print("ca chie ")
        exit(255)
      if ldapAction  == "add":
        print("Ajout de" + getIdFromDn(arguments.user) + "Values :  " +  str(convertLdapRecord(ldapRecord)))
        #pcCnx.addPapercutLscExec(arguments.user)
        #pcCnx.updatePapercutLscExec(arguments.user,convertLdapRecord(ldapRecord)))
      elif ldapAction == "modify":
        print("Modif de" + getIdFromDn(arguments.user) + "Values :  " +  str(convertLdapRecord(ldapRecord)))
        #pcCnx.updatePapercutLscExec(arguments.user,convertLdapRecord(ldapRecord)))
      elif ldapAction == "delete":
        print("Suppresion de" + getIdFromDn(arguments.user) + "Values :  " +  str(convertLdapRecord(ldapRecord)))
        #pcCnx.removePapercutLscExec(arguments.user)
      elif ldapAction == "modrdn":
        print("c'est un renomage")
      else:
        print("c'est autre chose")

#      print("c'est autre chose" + str(ldapRecord))
    except ValueError as e:
      print("c'est un getUSer")
      #pcCnx.getPapercutLscExec(arguments.user,sys.stdin)

