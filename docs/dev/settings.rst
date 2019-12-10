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
