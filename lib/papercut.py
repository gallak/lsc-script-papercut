#!/usr/bin/env python
# encoding: UTF-8
import sys
import logging
from pprint import pprint
from xmlrpc.client import ServerProxy, Fault, ProtocolError
from ssl import create_default_context, Purpose
import ldif

logger = logging.getLogger("pcLog")

#from ldap import modlist

#https://living-sun.com/fr/python/706390-python-ldap-lib-import-ldif-python-openldap-python-ldap.html

# This fonction translate RFID Tag read fromla a classic reader and store in supannCMSCard fielad
def fixCMSCarID(field,value):
   if field == "supannCMSCard":
       localTag=TAG("HEX",value)
       return(localTag.getPaperCutCard())
   else:
       return(value)



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
#        if limit == 0 or len(user_list) < limit:
#            print(" boucle et limitre de merde !!!!   ya perosne")
#            break # We have reached the end

        offset += limit # We need to next slice of users
        return_list += user_list
        if limit == 0 or len(user_list) < limit:
            #print(" boucle et limitre de merde !!!!   ya perosne")
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
      pprint(str(msg))


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
    pprint(str(msg))


#https://lsc-project.org/documentation/plugins/executable/howto_scripts
# IN  : nothing
# OUT :
##  dn: entry1 identifier
##  pivot1: aaa
# ARG : nothing
  def listPapercutLscExec(self):
    self.logger = logging.getLogger('pcLog.papercut.LIST')
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
  def getPapercutLscExec(self,dn,inputStream):
    self.logger = logging.getLogger('pcLog.papercut.GET')
    username = ''
    rdn=dn.split(",")[0].split('=')
    if rdn[0] == self.pivot:
      username=rdn[1]
    else:
      self.logger.debug(" no pivot values found ")
      exit(255)

    try:
      for l in inputStream:
        self.logger.debug("InputStream read: %s ",l)
        inputArray = l.strip().split(": ")
        self.logger.debug("Split %s to %s",l.strip(),str(inputArray))

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
  def addPapercutLscExec(self,dn,inputStream):
    self.logger = logging.getLogger('pcLog.papercut.ADD')
    modifTab=[]

    self.logger.debug("try to fetch pivot value from dn: %s",dn)
    rdn=dn.split(",")[0].split('=')
    if rdn[0] == self.pivot:
      username=rdn[1]
    else:
      self.logger.debug(" no pivot values found ")
      exit(255)
    self.logger.debug(" Create new user %s",username)
    try:
      self.proxy.api.addNewUser(self.token, username)
    except Exception as x:
      self.logger.debug("Unable tu create account %s : %s",username,str(x))
      exit(255)

    self.logger.debug("User %s created, currently fill it",username)

    inputData = ldif.LDIFRecordList(inputStream)
    inputData.parse()
    ldapRecord = inputData.all_records[0][1]

    for item in ["-","changetype","username","dn"]:
      try:
        del ldapRecord[item]
      except KeyError as x:
        self.logger.debug("No %s element to clean",item)

    for paperCutField in ldapRecord.keys():
      tab=[]
      self.logger.debug("Reading %s",  paperCutField)
      tab.append(paperCutField)
      tab.append(fixCMSCarID(paperCutField,ldapRecord[paperCutField][0].decode()))
      self.logger.debug("Element to add : %s ",str(tab))
      modifTab.append(tab)
    try: 
      self.proxy.api.setUserProperties(self.token, username, modifTab)
    except Exception as x:
      self.logger.debug("Problem  : %s ",str(x))
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

  def updatePapercutLscExec(self, dn,inputStream):
    self.logger = logging.getLogger('pcLog.papercut.UPDATE')

    modifTab=[]
    tab=[]

    self.logger.debug("try to fetch pivot value from dn: %s",dn)
    rdn=dn.split(",")[0].split('=')
    if rdn[0] == self.pivot:
      username=rdn[1]
    else:
      self.logger.debug(" no pivot values found ")
      exit(255)
    # read LDIF update send by LSC : mapping field between LSC and Ppaercut is assured by LSC Config
    inputData = ldif.LDIFRecordList(inputStream)
    inputData.parse_entry_records()
    ldapRecord=inputData.all_records[0][1]
    self.logger.debug("clean LDAP Record, keep only field to add or change")
    # username is trashed, username could be send for an update, only for a creation
    for item in ["-","replace","changetype","add","username"]:
      try:
        del ldapRecord[item]
      except KeyError as x:
        self.logger.debug("No %s element to clean",item)

    for paperCutField in ldapRecord.keys():
      tab=[]
      self.logger.debug("Reading %s",  paperCutField)
      tab.append(paperCutField)
      tab.append(fixCMSCarID(paperCutField,ldapRecord[paperCutField][0].decode()))
      self.logger.debug("Element to add : %s ",str(tab))
      modifTab.append(tab)
    try: 
      self.proxy.api.setUserProperties(self.token, username, modifTab)
    except Exception as x:
      self.logger.debug("Problem  : %s ",str(x))
      exit(255)



# IN  :
##  dn: DN
##  changetype: delete
# OUT : nothing
# ARG : script is called with the destination main identifier as argument.
  def removePapercutLscExec(self, username):
    self.logger = logging.getLogger('pcLog.papercut.REMOVE')

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
# ARG : script is called with the destination main identifier as argumen
##  def renamePapercutLscExec():




class TAG:
  tag=''
  typeTag=''

  def __init__(self,typeTag,tag):
    ''' Constructor for this class. '''
    self.typeTag=typeTag
    self.tag=tag

  mappingHpPrefix = {
    'DesfireV2' : "r007f0138",
    'MifareClassic' : "r007f0120",
  }


  def getPaperCutCard(self):
    if [ self.typeTag == "HEX" ]:
#      print("== TAG  :  " + self.tag + " v courte" + self.tag[0:9] + " " + self.tag[8:16])
      flag="00000000"
      prefix=self.tag[0:8]

      # test si mifare classic, les octaet de poid fort sont à 0
      if flag == prefix :
  #      print("  == le tag est un Mifare Classic")
        lowerTag=self.tag[8:16]
        tagConvert=lowerTag[6:8]+lowerTag[4:6]+lowerTag[2:4]+lowerTag[0:2]
        completeTag=self.mappingHpPrefix['MifareClassic'] + tagConvert

      else:
#        print("  == le tag est un Desfire")
        completeTag=self.mappingHpPrefix['DesfireV2'] + self.tag[2:]
 #     print("  == CARTE : " + completeTag)
    return(completeTag.upper())

