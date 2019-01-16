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

  user_settings: {
      orgunit: {
          show_location: true,
          show_roles: true,
          show_user_key: true
      }
  }

From this response, it is not possible to distinguish if the setting is local,
inherited or global.

OU specific settings
^^^^^^^^^^^^^^^^^^^^
The actual configuration options set directly on the OU, can be read from the
dedicated configuration api: ::

  curl http://localhost/service/ou/cc238af7-f00f-422f-a415-6fba0f96febd/get_configuration

The reply could be: ::
  {
      "show_user_key":"False"
  }

In this case the value for ''show_user_key'' will be read from this
configuration value, and the rest of the configuration options will be
inherited or read from global scope.

Global settings
^^^^^^^^^^^^^^^
The current global settings can also be read from the configuration api: ::

  curl http://localhost/service/o/get_configuration

With the reply: ::
  {
     show_location: "True",
     show_roles: "True",
     show_user_key: "True"
  }
  
Global settings are global for all organisations.


Writing configuration options
-----------------------------

The payload for updating global or OU-specific settings are identical:
  '''
  {
    "org_units":{
       "show_roles": "False"
       }
  }
  '''

Currently, there are only settings for org units and thus the outer key
will always be ''org_units''. It is possible to update more than one key pr
request.
  
Global settings
^^^^^^^^^^^^^^^
The update a global setting: ::

  curl -X POST -H "Content-Type: application/json" --data '{"org_units": {"show_roles": "False"}}' http://localhost/service/o/set_configuration

OU specific settings
^^^^^^^^^^^^^^^
To update or create a setting for a specific OU: ::
  curl -X POST -H "Content-Type: application/json" --data '{org_units": {"show_user_keys": "False"}}' http://localhost/service/ou/cc238af7-f00f-422f-a415-6fba0f96febd/set_configuration
