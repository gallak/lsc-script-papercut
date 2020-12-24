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

  # connection routing to PaperCut server
  def connect(self):
    try:
      self.proxy = ServerProxy(self.url + self.path, verbose=False,context = create_default_context(Purpose.CLIENT_AUTH))
      self.logger.info("CONNECT: Connection to %s",str(self.url+self.path))
    except all as error:
      self.logger.critical("CONNECT: Unable to connect to %s : %s ",str(self.url+self.path),str(error))

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
            self.logger.info("PC:listUserAccounts(): Return fault is %s",error.faultString)
            exit(1)
        except ProtocolError as error:
            self.logger.critical("PC:listUserAccounts(): A protocol error occurred to URL: %s nHTTP/HTTPS headers: %s Error code: %s Error message: %s",error.url, error.headers, error.errcode, error.errmsg)
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
        self.logger.warning("PC:getUserProperty():  Return fault is %s",error.faultString)
        exit(1)
    except xmlrpc.client.ProtocolError as error:
        self.logger.critical("PC:getUserProperty(): A protocol error occurred to URL: %s nHTTP/HTTPS headers: %s Error code: %s Error message: %s",error.url, error.headers, error.errcode,error.errmsg)
        exit(1)
    except Exception as x:
        self.logger.critical("PC:getUserProperty(): Error : %s",str(x))
        exit(1)

    return properties

  def show_all_user_details(self,attributs):
    for user in self.list_users():
      self.show_user_details(user,attributs)

  def show_user_details(self,user,attributs):
    msg=user
    properties=self.get_user_details(user,attributs)
    for value in properties:
        if value :
            msg = msg +";" + value
    pprint(str(msg))



