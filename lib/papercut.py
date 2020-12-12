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

  mapping         = {}
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
    for user in self.list_users():
        print("dn: " + user)
        print(self.pivot + ": " + user)
        print("")

# IN  :
##   pivot1: aaa
##   pivot2: xxx
# OUT :
##  dn: entry identifier
##  attribute1: aaa
##  attribute2: abc
##  attribute3: def
# ARG : nothing
  def getPapercutLscExec(self,inputStream):
    username = ''
    try:
#      fixe get username from inpustream  et  filtre avec l'attribut lsc-pivot
     # get attributs from mapping file
FIX input stream
      for l in inputStream:
        self.logger.debug("input read: %s ",l)
        line= l.rstrip()
        line.split()
        self.logger.debug("Split %s <=> %s ",line[0],line[1])
        if l[0] == self.pivot:
          username = l[1]
          break
        else :
          self.logger.debug("%s is not pivot attribut",l[0])
      if not username:
        self.logger.debug(" no pivot values found ")
        exit(255)
      else:
        self.logger.debug(" pivot value found : %s",l[1])

      self.get_user_details(username,mapping.values())
      print("dn: " + username)
      for index, value in enumerate(self.get_user_details(username,mapping.values())):
        if value :
           print(attributs[index]+": "+value)
    except Exception as x:
      self.logger.debug("Exception : %s",str(x))
      exit(255)

# IN  :
##  dn: DN
##  changetype: add
##  attribute1: aaa
##  attribute2: abc
##  attribute3: def
# OUT : nothing
# ARG : script is called with the destination main identifier as argument
  def addPapercutLscExec(self, username,inputStream):

    modifTab=[]
    inputData = ldif.LDIFRecordList(inputStream)
    inputData.parse()
    for ldapField, paperCutField in self.mapping.items():
        tab=[]
        try :
            valueLdapField = inputData.all_records[0][1][ldapField][0].decode()
        except KeyError as error:
            continue
        tab.append(paperCutField)
        tab.append(fixCMSCarID(ldapField,valueLdapField))
        modifTab.append(tab)
    try:
      self.proxy.api.addNewUser(self.token, username )
      self.proxy.api.setUserProperties(self.token, username, modifTab)
    except Exception as x :
      exit(255)
#      pprint(x)
#    pprint(modifTab)

# IN  : dn: DN
##   changetype: modify
##   replace: attribute1
##   attribute1: aaa
##   -
##   add: attribute2
##   attribute2: abc
# OUT : nothing
# ARG : script is called with the destination main identifier as argument.

  def updatePapercutLscExec(self, username,inputStream):
    modifTab=[]
    tab=[]
    inputData = ldif.LDIFRecordList(inputStream)
    inputData.parse_entry_records()

#    pprint(strinputStream)
#    pprint(inputData.all_records)

    for ldapField, paperCutField in self.mapping.items():
        tab=[]
        try :
            valueLdapField = inputData.all_records[0][1][ldapField][0].decode()
        except KeyError as error:
            continue
        tab.append(paperCutField)
        tab.append(fixCMSCarID(ldapField,valueLdapField))
        modifTab.append(tab)
    try: 
      self.proxy.api.setUserProperties(self.token, username, modifTab)
    except Exception as x:
     exit(255)
#     pprint(x)


# IN  :
##  dn: DN
##  changetype: delete
# OUT : nothing
# ARG : script is called with the destination main identifier as argument.
  def removePapercutLscExec(self, username):
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

