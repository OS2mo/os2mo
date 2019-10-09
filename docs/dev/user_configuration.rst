User configuration module
=========================

This section describes the runtime configuration of the frontend, to see the
configuration of the application on startup see :ref:`konfiguration`.

Front-end configuration
-----------------------

It is possible to perform simple configuration of the MO frontend using the
configuration module.

Setup
-----
To use the configuration module, suitable configuration must be set in the MO
configuration file, this will default to:

 * ``CONF_DB_NAME``: mora
 * ``CONF_DB_USER``: mora
 * ``CONF_DB_PASSWORD``: mora
 * ``CONF_DB_HOST``: localhost
 * ``CONF_DB_PORT``: 5432


Available options
-----------------
Currently, it is only possible to configure options for OUs. The currently
available options are:

* ``show_location`` Indicates whether the location of units should be visible
  in the top of the page.
* ``show_user_key`` Indicates whether the user key of units should be visible
  in the top of the page.
* ``show_roles`` Indicates whether the column ``Roller`` should be shown in
  the OU overview
* ``show_time_planning`` Indicates whether the time planning field should be
  enabled for OUs

If a option is identicated for a given unit, this will be used. If the option
is not available, it will inherit the value from the nearest parent in the
tree with the value set. If no parent has a value for the particular option,
a global value will be used.


Reading configuration options
-----------------------------

Currently active options
^^^^^^^^^^^^^^^^^^^^^^^^

The currently active options for a unit can be read directly from the API call
for the particular OU: ::

  curl http://localhost/service/ou/799aeaa4-129b-4f47-8632-1ee6ce987b21

Included in the response will be the options:

.. code-block:: json

   {
        "user_settings":{
            "orgunit":{
                "show_location":"True",
                "show_roles":"True",
                "show_user_key":"True",
                "show_time_planning":"True"
            }
        }
    }

From this response, it is not possible to distinguish if the option is local,
inherited or global.

OU specific options
^^^^^^^^^^^^^^^^^^^

The actual configuration options set directly on the OU, can be read from the
dedicated configuration api: ::

  curl http://localhost/service/ou/cc238af7-f00f-422f-a415-6fba0f96febd/configuration

The reply could be:

.. code-block:: json

    {
        "show_user_key":"False"
    }

In this case the value for ``show_user_key`` will be read from this configuration
value, and the rest of the configuration options will be inherited or read from
global scope.

Global options
^^^^^^^^^^^^^^

The current global options can also be read from the configuration api: ::

  curl http://localhost/service/o/configuration

With the reply:

.. code-block:: json

    {
       "show_location": "True",
       "show_roles": "True",
       "show_user_key": "True"
    }

Global options are global for all organisations.


Writing configuration options
-----------------------------

The payload for updating global or OU-specific settings are identical:

.. code-block:: json

    {
      "org_units":{
         "show_roles": "False"
         }
    }


Currently, there are only settings for org units and thus the outer key
will always be ``"org_units"``. It is possible to update more than one key per
request.

Global options
^^^^^^^^^^^^^^

To update a global options: ::

  curl -X POST -H "Content-Type: application/json" --data '{"org_units": {"show_roles": "False"}}' http://localhost/service/configuration

OU specific options
^^^^^^^^^^^^^^^^^^^^

To update or create a option for a specific OU: ::

  curl -X POST -H "Content-Type: application/json" --data '{org_units": {"show_user_keys": "False"}}' http://localhost/service/ou/cc238af7-f00f-422f-a415-6fba0f96febd/configuration
