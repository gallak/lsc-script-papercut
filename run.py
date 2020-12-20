#!/usr/bin/env python3
# https://pypi.org/project/randomuser/

import pprint
import logging
import sys
import os
from argparse import ArgumentParser
from lib import papercut
import ldif




# Logger creation
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
cliParser.add_argument("user", default="", help="username to use for get/updateOne/delete user from PAPERCUT server", type=str,nargs='?')

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
    #FIXME: faire la conversion de TAG
    data.append(val)
  return(data)


if __name__ == '__main__':
  pcCnx=papercut.PaperCut()
  # Init Class witch value
  pcCnx.url               =os.environ.get("LSC_PC_URL")
  pcCnx.token             =os.environ.get("LSC_PC_TOKEN")
  pcCnx.pivot             =os.environ.get("LSC_PC_PIVOT")
  pcCnx.papercutAttributs =os.environ.get("LSC_PC_ATTRIBUTS").split(",")
  pcCnx.connect()

  arguments = cliParser.parse_args()
  # If reading LDIF failed because it's malformed, it seems that implies a get Action
  # It seems than an empty input didn't throw an error at LDIFRecord and parse() functions
  try :
    inputData = ldif.LDIFRecordList(sys.stdin)
    inputData.parse()
    try :
      # If reading an empty record , an index errors occurs
      ldapRecord = inputData.all_records[0][1]
      try :
        ldapAction = ldapRecord['changetype'][0].decode()
      except Exception as e:
        logger.debug("Error while parsing stdin")
        exit(255)
      if ldapAction  == "add":
        logger.debug("Add %s with following values %s", pcCnx.getIdFromDn(arguments.user),str(convertLdapRecord(ldapRecord)))
        pcCnx.addPapercutLscExec(arguments.user)
        pcCnx.updatePapercutLscExec(arguments.user,convertLdapRecord(ldapRecord))
      elif ldapAction == "modify":
        logger.debug("Modify %s with following values %s", pcCnx.getIdFromDn(arguments.user),str(convertLdapRecord(ldapRecord)))
        pcCnx.updatePapercutLscExec(arguments.user,convertLdapRecord(ldapRecord))
      elif ldapAction == "delete":
        logger.debug("Delete %s ", pcCnx.getIdFromDn(arguments.user))
        pcCnx.removePapercutLscExec(arguments.user)
      elif ldapAction == "modrdn":
        logger.debug("Rename %s ", pcCnx.getIdFromDn(arguments.user))
        logger.debug("Not implemented yet")
      else:
        logger.debug("Unknowk Ldif action detected")
        exit(155)
    except IndexError as e:
      logger.debug("Error while parsing stdin %s",str(e))
      logger.debug("PC user list generation")
      pcCnx.listPapercutLscExec()
  except ValueError as e:
    logger.debug("Get information from %s", pcCnx.getIdFromDn(arguments.user))
    pcCnx.getPapercutLscExec(arguments.user)
