.. _Install-source:

========================
Installation from source
========================

This page describes the installation of OS2MO, :doc:`LoRa <mox:index>` and
Postgres on Ubuntu 18.04 without Docker. If you want a Docker based development
environment, see :ref:`dev-env`.


Postgres
========

Both OS2MO and LoRa need access to a database engine. LoRa need it for the main
storage, both LoRa and OS2MO share the :doc:`session database <mox:user/auth>`
and OS2MO needs it for :ref:`user_configuration`. The three different databases
do not need to be on the same database engine, but in this guide we will do so.

.. sidebar:: Reference

   `postgres-os2mo <https://hub.docker.com/r/magentaaps/postgres-os2mo>`_ Docker
   image and :ref:`LoRa database <mox:database>`.

The following use the default users, passwords and database names. They should
oblivious be changed in a production environment. Both here and in the
corresponding settings for LoRa and MO.

To install postgres and create the necessary databases and users:

.. code-block:: bash

   sudo apt-get update
   sudo apt-get install -y postgresql
   # mox db
   sudo -u postgres psql -v ON_ERROR_STOP=1 <<-EOSQL1
        create user mox with encrypted password 'mox';
        create database mox;
        grant all privileges on database mox to mox;
        alter database mox set search_path to actual_state, public;
        alter database mox set datestyle to 'ISO, YMD';
        alter database mox set intervalstyle to 'sql_standard';
        \connect mox
        create schema actual_state authorization mox;
        create extension if not exists "uuid-ossp" with schema actual_state;
        create extension if not exists "btree_gist" with schema actual_state;
        create extension if not exists "pg_trgm" with schema actual_state;
   EOSQL1
   # mora conf db
   sudo -u postgres psql -v ON_ERROR_STOP=1 <<-EOSQL2
        create user mora with encrypted password 'mora';
        create database mora owner mora;
        grant all privileges on database mora to mora;
   EOSQL2
   # sessions db
   sudo -u postgres psql -v ON_ERROR_STOP=1 <<-EOSQL3
        create user sessions with encrypted password 'sessions';
        create database sessions owner sessions;
        grant all privileges on database sessions to sessions;
   EOSQL3

For an explanation of the setup of the mox database see :ref:`LoRa database
<mox:database>`.


System packages
===============

.. sidebar:: Reference

   `Nodejs install
   <https://github.com/nodesource/distributions/blob/master/README.md#debinstall>`_
   and `Yarn install
   <https://classic.yarnpkg.com/en/docs/install/#debian-stable>`_.

The following will install node, python and LoRas and OS2MOs one system
dependency.

.. code-block:: bash

   curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
   echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
   curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
   sudo apt-get install -y nodejs yarn python3-dev python3-venv libxmlsec1-dev


LoRA
====

.. sidebar:: Reference

   :doc:`LoRa installation <mox:user/installation>`.

The following will clone the LoRa repo, create a :ref:`virtual environment
<python:tut-venv>` and install the LoRa python requirements. Finally, it will
initialize the mox database.

.. code-block:: bash


   git clone https://github.com/magenta-aps/mox.git
   cd mox
   # git checkout development
   python3 -m venv venv
   source venv/bin/activate
   pip install -U pip
   cd oio_rest
   pip install -r requirements.txt
   pip install .

   python3 -m oio_rest initdb
   deactivate && cd ~

OS2MO
=====

The following will clone the OS2MO repo, install frontend dependencies, build
the frontend, create a :ref:`virtual environment <python:tut-venv>` and install
the OS2MO python requirements.

.. code-block:: bash

   git clone https://github.com/OS2mo/os2mo.git
   cd os2mo
   # git checkout development
   cd frontend
   yarn install
   yarn build
   cd ..
   python3 -m venv venv
   source venv/bin/activate
   pip install -U pip
   cd backend
   pip install -r requirements.txt
   pip install .

Create a settings file, :file:`~/os2mo/user-settings.toml`, with the following
content. More options are available here: :ref:`Settings`.

.. code-block:: toml
   :caption: :file:`~/os2mo/user-settings.toml`

   dummy_mode = true

Finally, set the configuration file and flask app environment variables and
initialize the configuration database.

.. code-block:: bash

   export OS2MO_USER_CONFIG_PATH=~/os2mo/user-settings.toml
   export FLASK_APP=mora.app:create_app

   python3 -m mora.cli initdb
   deactivate && cd ~


Starting the services
=====================

The services should now be ready to start. Run the following in two different
terminals:

.. code-block:: bash
   :caption: LoRa

   cd mox
   source venv/bin/activate
   python3 -m oio_rest run -h 0.0.0.0 -p 8080

.. code-block:: bash
   :caption: OS2MO

   cd os2mo
   source venv/bin/activate
   cd backend
   export OS2MO_USER_CONFIG_PATH=~/os2mo/user-settings.toml
   python3 -m mora.cli run -h 0.0.0.0 -p 5000

You can now access OS2MO on http://localhost:5000.
