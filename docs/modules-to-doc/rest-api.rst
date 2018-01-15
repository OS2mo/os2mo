HTTP REST API
=============


.. qrefflask:: mora.app:app
   :blueprints: authentication, api
   :order: path


Service layer
-------------

.. autoflask:: mora.app:app
   :include-empty-docstring:
   :blueprints: api
   :groupby: view


Authentication
--------------

.. autoflask:: mora.app:app
   :include-empty-docstring:
   :blueprints: authentication
   :groupby: view
