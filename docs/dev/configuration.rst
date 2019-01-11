Configuration module
=====================

Front-end configuration
-----------------------

It is possible to perform simple configuration of the MO frontend using the
configuration module. 

Setup
-----
To use the configuration module, suitable credentials must be set in the MO
configuration file, these will default to:
* USER_SETTINGS_DB_NAME: mora
* USER_SETTINGS_DB_USER: mora
* USER_SETTINGS_DB_PASSWORD: mora
* USER_SETTINGS_DB_HOST: localhost

Available settings
------------------
Currently, it os only possible to configure settings for OUs. The currently
available options are:

* ``show_location`` Indicates whether the location of units should be visible
  in the top of the page.
* ``show_user_key`` Indicates whether the user key of units should be visible
  in the top of the page.
* ``show_roles`` Indicates whether the column ``Roller`` should be shown in
  the OU overview

If a settings is identicated for a given OU, this will be used. If the setting
is not available, it will inherit the value from the nearest parent in the
tree with the value set. If no parents has a value for the particular setting,
a global value will be used.

Setting configuration options
-----------------------------

Reading configuration options
-----------------------------

Currently activce settings
^^^^^^^^^^^^^^^^^^^^^^^^^^
The currently active settings for a unit can be read directly from the API call
for the particular OU: ::

  curl http://localhost/service/ou/.....

Included in the response will be the settings: ::

  setting ... wait for data

From this response, it is not possible to distinguish if the setting is local,
inherited or global.

OU specific settings
^^^^^^^^^^^^^^^^^^^^
The actual configuration options set directly on the OU, can be read from the
dedicated configuration api: ::

  curl http://localhost/service/ou/...../get_configuration

Reply ....


Global settings
^^^^^^^^^^^^^^^
The current global settings can also be read from the configuration api: ::

  curl http://localhost/service/o/get_configuration

Reply ....

Global settings are global for all organisations.


Writing configuration options
-----------------------------

The payload for updating global or OU-specific settings are identical:
  '''
  {
    org_units":{
       "show_roles": "False"
       }
  }
  '''

Currently, only there are only settings for org units and thus the outer key
will alwayys be ''org_units''. It is possible to update more than one key pr
request.
  
Global settings
^^^^^^^^^^^^^^^
The update a global setting: ::

  curl -X POST -H "Content-Type: application/json" --data '{org_units": {"show_roles": "False"}}' http://localhost/service/o/set_configuration

OU specific settings
^^^^^^^^^^^^^^^
To update or create a setting for a specific OU: ::
  curl -X POST -H "Content-Type: application/json" --data '{org_units": {"show_user_keys": "False"}}' http://localhost/service/ou/...../set_configuration
