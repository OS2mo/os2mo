Configuration module
=====================

Front-end configuration
-----------------------

It is possible to perform simple configuration of the MO frontend using the
configuration entry ``USER_SETTINGS``.

This entry could look something like this:

.. sourcecode:: json

    {
        "orgunit": {
            "show_location": true,
            "show_roles": true,
            "show_bvn": true,
            "927dc4d5-fdca-4062-a0d8-a44e8a9e8685": {
                "show_location": true,
                "show_roles": false,
                "show_user_key": false
            }
        }
    }


The general key orgunit indicates that the settings apply to organisational
units (currently no settings are possible for employees). Three different
settings can be applied:

* ``show_location`` Indicates whether the location of units should be visible
  in the top of the page.
* ``show_user_key`` Indicates whether the user key of units should be visible
  in the top of the page.
* ``show_roles`` Indicates whether the column ``Roller`` should be shown in
  the OU overview.

It is possible to perform configuration on sub-trees by indicating the same
keys as sub-keys in the json structure. In the above example, all units in
the sub-tree rooted in ``927dc4d5-fdca-4062-a0d8-a44e8a9e8685`` will have
a configuration separate from the rest of the units.
