#!/usr/bin/env python
# encoding: UTF-8
import sys
import logging
from pprint import pprint
from xmlrpc.client import ServerProxy, Fault, ProtocolError
from ssl import create_default_context, Purpose
from lib.papercut import PaperCut
import ldif

# a new class LscPaperCut based on PaperCut is used for creating all scritps for make un sync link between LDAP and a Papercut server
# see : https://lsc-project.org/documentation/plugins/executable/howto_scripts


logger = logging.getLogger("pcLog")

class LscPaperCut(PaperCut):

  # extract username and check if it's the pivot attribut
  def getIdFromDn(self,dn):
    username = ''
    rdn=dn.split(",")[0].split('=')
    if rdn[0] == self.pivot:
      return(rdn[1])
    else:
      logger.debug("No pivot values found ")
    exit(255)


  # IN  : nothing
  # OUT :
  ##  dn: entry1 identifier
  ##  pivot1: aaa
  # ARG : nothing
  def listPapercutLscExec(self):
    logPrefix="LIST"
    for username in self.list_users():
      print("dn: " + self.pivot + "=" + username + ",ou=fake,dc=dn")
      print(self.pivot + ": " + username)
      print("")
      self.logger.debug("%s: user returned %s ", logPrefix,username)

  # IN  :
  ##   pivot1: aaa
  ##   pivot2: xxx
  # OUT :
  ##  dn: entry identifier
  ##  attribute1: aaa
  ##  attribute2: abc
  ##  attribute3: def
  # ARG : nothing
  # FIXME normally pivot attribut and their  values are fetch from input

  def getPapercutLscExec(self,dn):
    logPrefix="GET"
    try:
      username = self.getIdFromDn(dn)
      self.logger.debug("%s: Request %s for user %s",logPrefix,str(self.papercutAttributs),username)
      fetchedValues=self.get_user_details(username,self.papercutAttributs)

      print("dn: " + dn)
      i=0
      while i < len(self.papercutAttributs):
        if fetchedValues[i]:
          print(self.papercutAttributs[i] + ": " + fetchedValues[i])
          self.logger.debug("%s: %s is %s",logPrefix,self.papercutAttributs[i], fetchedValues[i])
        i+=1
    except Exception as x:
      self.logger.debug("%s: Exception : %s, %s shouldn't exist",logPrefix,str(x),username)
    exit(0)

  # IN  :
  ##  dn: DN
  ##  changetype: add
  ##  attribute1: aaa
  ##  attribute2: abc
  ##  attribute3: def
  # OUT : nothing
  # ARG : script is called with the destination main identifier as argument
  def addPapercutLscExec(self,dn):
    logPrefix="ADD"
    username = self.getIdFromDn(dn)
    self.logger.debug("%s: Create new user %s",logPrefix,username)
    try:
      self.proxy.api.addNewUser(self.token, username)
    except Exception as x:
      self.logger.debug("%s: Unable tu create account %s : %s",logPrefix,username,str(x))
      exit(255)


  # IN  : dn: DN
  ##   changetype: modify
  ##   replace: attribute1
  ##   attribute1: aaa
  ##   -
  ##   add: attribute2
  ##   attribute2: abc
  # OUT : nothing
  # ARG : script is called with the destination main identifier as argument.

  def updatePapercutLscExec(self,dn,values):
    logPrefix = "UPDATE"
    username = self.getIdFromDn(dn)
    try:
      self.logger.debug("%s: Update %s with %s",logPrefix,username,str(values))
      self.proxy.api.setUserProperties(self.token, username, values)
    except Exception as x:
      self.logger.debug("%s: Problem  : %s ",logPrefix,str(x))
      exit(255)



  # IN  :
  ##  dn: DN
  ##  changetype: delete
  # OUT : nothing
  # ARG : script is called with the destination main identifier as argument.
  def removePapercutLscExec(self, dn):
    logPrefix = "REMOVE"
    username = self.getIdFromDn(dn)
    try:
      self.proxy.api.deleteExistingUser(self.token, username)
    except Exception as x:
      self.logger.debug("%s: Problem  : %s ",logPrefix,str(x))
      exit(255)

  # IN  :
  ##  dn: DN
  ##  changetype: modrdn
  ##  newrdn: attribute1=aaa
  ##  deleteoldrdn: 1
  ##  newsuperior: BRANCH
  # OUT :
  ##  dn: entry1 identifier
  ##  pivot1: aaa
  # ARG : script is called with the destination main identifier as argument
  ##  def renamePapercutLscExec():


