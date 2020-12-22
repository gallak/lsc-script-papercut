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
    self.logger.debug("creation de l'objet")


  def connect(self):
    try:
      self.proxy = ServerProxy(self.url + self.path, verbose=False,context = create_default_context(Purpose.CLIENT_AUTH))
      self.logger.debug("Connexion")
    except all as error:
      pprint.pprint(error)

  def getIdFromDn(self,dn):
    username = ''
    rdn=dn.split(",")[0].split('=')
    if rdn[0] == self.pivot:
      return(rdn[1])
    else:
      logger.debug(" no pivot values found ")
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
            print("\ncalled listUserAccounts(). Return fault is {}".format(error.faultString))
            exit(1)
        except ProtocolError as error:
            print("\nA protocol error occurred\nURL: {}\nHTTP/HTTPS headers: {}\nError code: {}\nError message: {}".format(
                error.url, error.headers, error.errcode, error.errmsg))
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
        print("\ncalled getUserProperty(). Return fault is {}".format(error.faultString))
        exit(1)
    except xmlrpc.client.ProtocolError as error:
        print("\nA protocol error occurred\nURL: {}\nHTTP/HTTPS headers: {}\nError code: {}\nError message: {}".format(error.url, error.headers, error.errcode, error.errmsg))
        exit(1)
    except Exception as x:
        pprint(x)

    return properties

  def show_all_user_details(self,attributs):
    for user in self.list_users():
      msg=user
      try:
          properties = self.proxy.api.getUserProperties(self.token,user,attributs)
      except xmlrpc.client.Fault as error:
          print("\ncalled getUserProperty(). Return fault is {}".format(error.faultString))
          exit(1)
      except xmlrpc.client.ProtocolError as error:
          print("\nA protocol error occurred\nURL: {}\nHTTP/HTTPS headers: {}\nError code: {}\nError message: {}".format(error.url, error.headers, error.errcode, error.errmsg))
          exit(1)
      for value in properties:
          if value :
              msg = msg +";" + value
      #pprint(str(msg))


  def show_user_details(self,user,attributs):
    msg=user
    try:
        properties = self.proxy.api.getUserProperties(self.token,user,attributs)
    except xmlrpc.client.Fault as error:
        print("\ncalled getUserProperty(). Return fault is {}".format(error.faultString))
        exit(1)
    except xmlrpc.client.ProtocolError as error:
        print("\nA protocol error occurred\nURL: {}\nHTTP/HTTPS headers: {}\nError code: {}\nError message: {}".format(error.url, error.headers, error.errcode, error.errmsg))
        exit(1)
    for value in properties:
        if value :
            msg = msg +";" + value
    #pprint(str(msg))






#https://lsc-project.org/documentation/plugins/executable/howto_scripts
# IN  : nothing
# OUT :
##  dn: entry1 identifier
##  pivot1: aaa
# ARG : nothing
  def listPapercutLscExec(self):
    #self.logger = logging.getLogger('pcLog.papercut.LIST')
    for username in self.list_users():
      print("dn: " + self.pivot + "=" + username + ",ou=fake,dc=dn")
      print(self.pivot + ": " + username)
      print("")
      self.logger.debug("user returned %s ", username)

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
    #self.logger = logging.getLogger('pcLog.papercut.GET')

    try:
      username = self.getIdFromDn(dn)
      self.logger.debug("Request %s for user %s",str(self.papercutAttributs),username)
      fetchedValues=self.get_user_details(username,self.papercutAttributs)

      print("dn: " + dn)
      i=0
      while i < len(self.papercutAttributs):
        if fetchedValues[i]:
          print(self.papercutAttributs[i] + ": " + fetchedValues[i])
          self.logger.debug("%s is %s",self.papercutAttributs[i], fetchedValues[i])
        i+=1
    except Exception as x:
      self.logger.debug("Exception : %s, %s shouldn't exist",str(x),username)
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
    #self.logger = logging.getLogger('pcLog.papercut.ADD')

    username = self.getIdFromDn(dn)
    self.logger.debug("Create new user %s",username)
    try:
      self.proxy.api.addNewUser(self.token, username)
    except Exception as x:
      self.logger.debug("Unable tu create account %s : %s",username,str(x))
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
    #self.logger = logging.getLogger('pcLog.papercut.UPDATE')
    username = self.getIdFromDn(dn)
    try:
      self.logger.debug("Update %s with %s",username,str(values))
      self.proxy.api.setUserProperties(self.token, username, values)
    except Exception as x:
      self.logger.debug("Problem  : %s ",str(x))
      exit(255)



# IN  :
##  dn: DN
##  changetype: delete
# OUT : nothing
# ARG : script is called with the destination main identifier as argument.
  def removePapercutLscExec(self, dn):
    self.logger = logging.getLogger('pcLog.papercut.REMOVE')
    username = self.getIdFromDn(dn)
    try:
      self.proxy.api.deleteExistingUser(self.token, username)
    except Exception as x:
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


