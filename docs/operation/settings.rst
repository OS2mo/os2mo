.. _Settings:

========
Settings
========

OS2mo has various configurable parameters. This file describes how to
configure the program. There are default settings, as shown in
:file:`backend/mora/default-settings.toml`. These can be overwritten by
two files that you can point to with environment variables:


.. py:data:: OS2MO_SYSTEM_CONFIG_PATH

    Path to a toml settings file. This overwrites the default settings, but has
    lower precedence than :data:`OS2MO_USER_CONFIG_PATH`. The purpose of this
    file is to configure environments. We use it for docker.


.. py:data:: OS2MO_USER_CONFIG_PATH

    Point this to a toml file with your desired settings. The settings in this
    file have the highest precedence.


This is the content of :file:`backend/mora/default-settings.toml`:

.. literalinclude:: ../../backend/mora/default-settings.toml
    :language: toml
    :lines: 9-


The :code:`[[navlinks]]` setting can contain one or more links. These links will be
visible from a "Links" menu in the MO top navigation. Here is an example:

.. code::

    [[navlinks]]
    href = "https://google.com"
    text = "Google"

    [[navlinks]]
    href = "https://magenta.dk"
    text = "Magenta"

See the TOML documentation on
`arrays of tables <https://toml.io/en/v1.0.0#array-of-tables>`_ for more
details on the syntax used.
