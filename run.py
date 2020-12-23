#!/usr/bin/env python3

import pprint
import logging
import sys
import os
#from lib import lscPapercut
import ldif
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + './lib/')
#from lib import papercut
from lib import LscConnector


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
    data.append(val)
  return(data)


if __name__ == '__main__':
  #pcCnx=papercut.PaperCut()
  pcCnx=LscConnector.LscPaperCut()
  # Init Class witch value
  pcCnx.url               =os.environ.get("LSC_PC_URL")
  pcCnx.token             =os.environ.get("LSC_PC_TOKEN")
  pcCnx.pivot             =os.environ.get("LSC_PC_PIVOT")
  pcCnx.papercutAttributs =os.environ.get("LSC_PC_ATTRIBUTS").split(",")
  pcCnx.connect()

  if len(sys.argv) > 2 :
    logger.debug("Too much arguments")
    exit(255)

  try:
    user = sys.argv[1]
    try :
      inputData = ldif.LDIFRecordList(sys.stdin)
      inputData.parse()
      ldapRecord = inputData.all_records[0][1]
      try :
        ldapAction = ldapRecord['changetype'][0].decode()
      except Exception as e:
        logger.debug("Error while parsing stdin")
        exit(255)
      if ldapAction  == "add":
        logger.debug("Add %s with following values %s", pcCnx.getIdFromDn(user),str(convertLdapRecord(ldapRecord)))
        pcCnx.addPapercutLscExec(user)
        pcCnx.updatePapercutLscExec(user,convertLdapRecord(ldapRecord))
      elif ldapAction == "modify":
        logger.debug("Modify %s with following values %s", pcCnx.getIdFromDn(user),str(convertLdapRecord(ldapRecord)))
        pcCnx.updatePapercutLscExec(user,convertLdapRecord(ldapRecord))
      elif ldapAction == "delete":
        logger.debug("Delete %s ", pcCnx.getIdFromDn(user))
        pcCnx.removePapercutLscExec(user)
      elif ldapAction == "modrdn":
        logger.debug("Rename %s ", pcCnx.getIdFromDn(user))
        logger.debug("Not implemented yet")
      else:
        logger.debug("Unknown Ldif action detected")
        exit(155)
    except Exception as e:
      logger.debug("Get PaperCut informations for %s", pcCnx.getIdFromDn(user))
      pcCnx.getPapercutLscExec(user)
  except IndexError as e:
    logger.debug("Fetch all user from PaperCut")
    pcCnx.listPapercutLscExec()
