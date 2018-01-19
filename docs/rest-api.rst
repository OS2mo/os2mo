REST API
========


.. qrefflask:: mora.app:app
   :blueprints: service, authentication, api


Service layer
-------------

.. autoflask:: mora.app:app
   :include-empty-docstring:
   :blueprints: service


Authentication
--------------

.. autoflask:: mora.app:app
   :include-empty-docstring:
   :blueprints: authentication
   :groupby: view


Legacy service layer
--------------------

.. autoflask:: mora.app:app
   :include-empty-docstring:
   :blueprints: api
   :groupby: view
