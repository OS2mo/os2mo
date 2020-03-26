Read-only
---------

Change the read-only status of the OS2mo UI.
The status only prevents creates/edits from the OS2mo UI.

This endpoints is meant to be used while importing data into OS2mo.
When imports fail, it often results in a rollback of the previous day's data,
meaning that all changes done to the system in between will be lost.

The intended use, is to enable read-only mode when an import starts, and only
deactivate it again once the system is in another "safe" state.

.. automodule:: mora.readonly

.. qrefflask:: mora.app:create_app()
   :blueprints: read_only
   :order: path

.. autoflask:: mora.app:create_app()
   :include-empty-docstring:
   :order: path
   :blueprints: read_only

.. Indices and tables
   ==================

   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`
