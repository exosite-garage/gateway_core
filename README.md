================================================================================
About Gateway_core
================================================================================

The gateway_core is an Exosite one platform gateway application with following features: 

* Automatically activate device client in one platform given proper Vendor/Model/SerialNumber.
* Download user application stored in one platform and launch the application.
* Manage/monitor multiple user applications.
* Restart individual application under user's control.
* Remotely restart the gateway_core.
* Ability to upgrade gateway_core itself.

License is BSD, Copyright 2012, Exosite LLC (see LICENSE file)

================================================================================
QUICK START
================================================================================

1. Create a new clonable device with whatever data sources are appropriate.

2. In the cloned device, also create a data source using "command" as the alias.

3. Create a new Client Model, using the `RID` of the above device.

4. Add some valid serial numbers to the Client Model

5. Edit "options.cfg" to have correct values based on your Client Model.
   Update the other items to suit:

  [setup]  
  vendor_name = VENDOR_NAME  
  model_name = MODEL_NAME  
  interface_type = NETWORK_INTERFACE*  
  uuid_file = UUID_FILE_LOCATION*  
  check_interval = 5  
  onep_server = m2.exosite.com  
  onep_port = 80  
  activate_url = /provision/activate  
  activate_timeout = 600  
  rpc_url = /api:v1/rpc/process  
  http_timeout = 3  
  datastore_interval = 3  
  app_id = gateway_core  
  log_level = info  
  
  --) NETWORK_INTERFACE can be set to 'eth0' or 'uuid'. If eth0 is used,
      add the MAC address of localhost as a serial number and add a device with
      that serial number. No need to change uuid file location.

  --) If 'uuid' is used as network interface, the uuid_file must be specified to
      indicate the file contaning uuid information structure like:

     [UUID]  
     uuid = 01234UUIDVALUE01234

  [network]  
  platform = janus_400ap  
  network_type = NETWORK_TYPE  
  ping_ip = IP_TO_PING  
  ping_interval = PING_INTERVAL  
  ping_retry = RETRY_COUNT  

  The [network] section is configured to monitor/auto-recover network.
  Currently, this is available only on 'janus_400ap' platform. The core
  will ping the IP_TO_PING for every PING_INTERVAL seconds, if it failed
  for RETRY_COUNT times, then core will try to restart the network.
  The NETWORK_TYPE could be 'gsm' or 'cdma'

6. Modify the gateway_core_options.cfg file to suit:  
    --) Add any apps the system shoud load to the apps_list line, separating
    the apps by a comma.  The section header MUST match the app_id (
    (above) with the suffix '_config'.  If any apps are added or removed
    from the apps_list, the gateway_core will start or stop the added
    or removed apps, respectively:

   [gateway_core_config]  
   apps_list = app1, app2, app3

    --) Set the gateway_core version number as desired.  The gateway_core
    will try to update itself and then reboot the entire system if it
    finds that its version number changed:

  [gateway_core_config]  
  version = 1

    --) If desired, add a config section for each app.  The section header
    must be named the same name as in the apps_list with the suffix of
    "_config".  The gateway_core will restart the app if it finds that
    the "version" parameter changes.

  [app1_config]  
  version = 1.0


7. Upload the gateway_core_options.cfg file as a content file named
   "gateway_core_options" to the Client Model you created

8. The "apps_template" folder contains example of simple app called
   "template.py".  Use this to create your own apps.

9. Upload your apps to the Client Model as content files, naming them
   with the same name as you listed in the options file above

10. Start running gateway_core:

   $python ./boot.pyc

For Your Information:  
* To reset gateway_core, send 'reset' to the 'command' dataport under the
  provisioned device.

* The "apps" folder will be used to store the application script at run time
  and should not be modified by user.

* The provisioned CIK for each individual device is stored in a hidden
  file called ".exosite" in the python folder.  This file can be read
  by the gateway_core app as well as your worker apps.

* To support update gateway_core itself. First tar *.pyc files as
  "gateway_core.tar" and upload it as a content file named "gateway_core".

    tar cvf gateway_core.tar *.pyc

* Each application should implement its own configuration management.
  For example, each application could read from a datasource under
  the device with the same name as the app_name (e.g. "template").
  This data source could store configuration information in json
  format that each app would use to self-modify its behavior based
  on the configuration of the specific device it is running on.  For
  example, the datasource could contain:

  {
    CUSTOMIZED_CONFIG_DATA,
    "monitor":{"name":MONITOR_NAME}
  }


================================================================================
Gateway Application Development Guideline
================================================================================

1) To develop gateway application, the application should be written in python
   and must define a global function named 'main' with an optional argument
   'wdtobject'.

2) Watch Dog Timer:
   To support this feature, you can edit "watch_dog_timer" line in the application
   config section and give it a number in seconds that is the communication timer
   between gateway_core and appication. If 0 is set, this feature is not enabled.
   Also this number should be greater than the time interval in your loop.
   For example.

     def main(wtdobj=None):
     while True:
       [Do something]
       time.sleep(30)

   then, the watch_dog_timer should be set to be greater than 30.

   [template_config]  
   watch_dog_timer = 35

   The following code should be executed before time.sleep() is called.

    wdtobj.sendMessage(os.getpid())

3) Graceful shutdown:
   When you enbale "Watch Dog Timer", this feature is also enabled. The following
   code should be inserted berore starting application loop.

    appproxy.signalShutdownEvent(kill_app)

   The kill_app is a global list which has single element 'False'.

  Full application example code:

    kill_app = [False]
    def main(wdtobj=None):
    global kill_app
    appproxy.signalShutdownEvent(kill_app)
    while False == kill_app[0]:
      print "This is an empty loop"
      wdtobj.sendMessage(os.getpid())
      time.sleep(10)

4) Starting and Restarting Applications:  
   * Write python code and save it as APP_NAME.py.  
   * Upload it as a content file named APP_NAME.  
   * Edit 'apps_list' to append this APP_NAME in 'gateway application option file'
     and add new config section [APP_NAME_config] for APP_NAME.
       
    [gateway_core_config]  
    version = 1  
    apps_list = APP_NAME

    [APP_NAME_config]  
    watch_dog_timer = 15  
    version = 1.0
  
   * upload this config file.  

  For 'gateway application option file', please refer to step 6 in Installation.

  To restart application, modify 'version' as below and upload again.

  [APP_NAME_config]  
  version = 2.0

5) To restart gateway_core, send 'reset' to the 'command' dataport under the
   provisioned device.

================================================================================
End Of File
