#==============================================================================
# template.py
# The is a template to start coding other apps that are part of the
# gateway core application framework.
#==============================================================================
##
## Tested with python 2.6
##
## Copyright (c) 2011, Exosite LLC
## All rights reserved.
##
import sys, time, os
import appproxy
from onepv1lib.datastore import Datastore
from onepv1lib.provision import Provision

kill_app = [False]

#===============================================================================
def main(wdtobj=None):
#===============================================================================
  global kill_app
  utility = UtilityFunctions()
  #print "Reading from Exosite:",utility.readData("status")
  #print utility.getModelContent('template')
  ### Uncomment following line if 'watch_dog_timer' in app option file is setup to > 0.
  appproxy.signalShutdownEvent(kill_app)
  while False == kill_app[0]:
    try:
      print "This is an empty loop. pid:", os.getpid()
      #utility.writeData("test", 6)
      ### Uncomment following line if 'watch_dog_timer' in app option file is setup to > 0.
      wdtobj.sendMessage(os.getpid())
      time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
      kill_app[0] = True
  print "Leaving application"

#===============================================================================
def stop():
#===============================================================================
  global kill_app
  kill_app = True

#===============================================================================
class UtilityFunctions():
#===============================================================================
  def __init__(self):
    self._conparams = {'onep_server':'m2.exosite.com','onep_port':"80",'rpc_url':'/api:v1/rpc/process', 'http_timeout':3, 'datastore_interval':3}
    self._modelparams = {'vendor_name':'intime','model_name':'intime_gateway'}
    self._cik = self._readCIK()
    self._datastore = None
    self._initDataStore()
    self._prov = Provision('http://' + self._conparams["onep_server"]
                           + ':' + self._conparams["onep_port"])

#========================== public methods =====================================
#-------------------------------------------------------------------------------
  def getCIK(self):
    return self._cik

  def writeData(self, alias, value):
    try:
      return self._datastore.write(alias, value)
    except:
      pass
#-------------------------------------------------------------------------------
  def readData(self, alias):
    try:
      return self._datastore.read(alias)
    except:
      pass

#-------------------------------------------------------------------------------
  def getModelContent(self,contentname):
    return self._getContent(contentname)

#========================== private methods ====================================
#------------------------------------------------------------------------------
  def _readCIK(self):
    path = ".exosite"
    if os.path.isfile(path):
      try:
        file = open(path)
      except:
        print "CIK file not found"
        return None
      cik = file.read()
      file.close()
      if len(cik) == 40:
        return cik
      else:
        print "Invalid CIK (length)"
        return None
    else:
      print "CIK file not found"
      return None

#------------------------------------------------------------------------------
  def _initDataStore(self):
    transport_config = {
                        'host':self._conparams['onep_server'],
                        'port':self._conparams['onep_port'],
                        'url': self._conparams['rpc_url'],
                        'timeout':self._conparams['http_timeout']
                       }
    if None != self._cik:
      self._datastore = Datastore(
                                  self._cik,
                                  self._conparams['datastore_interval'],
                                  autocreate={'format':'integer', 'preprocess':[], 'count':'infinity', 'duration':'infinity', 'visibility':'parent'},
                                  transport=transport_config
                                 )
      self._datastore.start()

#------------------------------------------------------------------------------
  def _getContent(self,contentid):
    return self._prov.content_download(
                                       self.getCIK(),
                                       self._modelparams["vendor_name"],
                                       self._modelparams["model_name"],
                                       contentid
                                      )

#===============================================================================
if __name__ == '__main__':
  try:
    main()
  except (KeyboardInterrupt, SystemExit):
    sys.exit(0)
  finally:
    stop()


