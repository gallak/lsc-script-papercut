#!/usr/bin/env python
# encoding: UTF-8
import sys
import logging
from pprint import pprint
from xmlrpc.client import ServerProxy, Fault, ProtocolError
from ssl import create_default_context, Purpose
import ldif

logger = logging.getLogger("pcLog")

class PaperCut:

  url             = 'http://papercut.site'
  token           = 'xxxxxxxxxxxxxxxxxxx'
  path            = 'rpc/api/xmlrpc'
  debug           = ''
  proxy           =''

  papercutAttributs = []
  pivot           = ''
  logger	  = ''

  def __init__(self):
    ''' Constructor for this class. '''
    self.logger = logging.getLogger('pcLog.papercut')
    self.logger.debug("INIT: creation de l'objet")

  # connection routien to PaperCut server
  def connect(self):
    try:
      self.proxy = ServerProxy(self.url + self.path, verbose=False,context = create_default_context(Purpose.CLIENT_AUTH))
      self.logger.debug("CONNECT: Connection to %s",str(self.url+self.path))
    except all as error:
      self.logger.debug("CONNECT: Unable to connect to %s : %s ",str(self.url+self.path),str(error))

  # extract username and check if it's the pivot attribut)
  def getIdFromDn(self,dn):
    username = ''
    rdn=dn.split(",")[0].split('=')
    if rdn[0] == self.pivot:
      return(rdn[1])
    else:
      logger.debug("No pivot values found ")
    exit(255)



  # retourne user list
  def list_users(self):
    offset = 0
    limit = 100
    counter = 0
    unknown_list = []
    return_list=[]

    while True:
        try:
            user_list = self.proxy.api.listUserAccounts(self.token, offset,limit)
        except Fault as error:
            self.logger.debug("PC:listUserAccounts(): Return fault is %s",error.faultString)
            exit(1)
        except ProtocolError as error:
            self.logger.debug("PC:listUserAccounts(): A protocol error occurred to URL: %s nHTTP/HTTPS headers: %s Error code: %s Error message: %s",error.url, error.headers, error.errcode, error.errmsg)
            exit(1)
        offset += limit # We need to next slice of users
        return_list += user_list
        if limit == 0 or len(user_list) < limit:
            break # We have reached the end

    return return_list

  def get_user_details(self,user,attributs):
    try:
        properties = self.proxy.api.getUserProperties(self.token,user,attributs)
    except xmlrpc.client.Fault as error:
        self.logger.debug("PC:getUserProperty():  Return fault is %s",error.faultString)
        exit(1)
    except xmlrpc.client.ProtocolError as error:
        self.logger.debug("PC:getUserProperty(): A protocol error occurred to URL: %s nHTTP/HTTPS headers: %s Error code: %s Error message: %s",error.url, error.headers, error.errcode,error.errmsg)
        exit(1)
    except Exception as x:
        self.logger.debug("PC:getUserProperty(): Error : %s",str(x))
        exit(1)

    return properties

  def show_all_user_details(self,attributs):
    for user in self.list_users():
      self.show_user_details(user,attributs)

  def show_user_details(self,user,attributs):
    msg=user
    properties=self.get_user_details(user,attributs):
    for value in properties:
        if value :
            msg = msg +";" + value
    pprint(str(msg))






#https://lsc-project.org/documentation/plugins/executable/howto_scripts
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


