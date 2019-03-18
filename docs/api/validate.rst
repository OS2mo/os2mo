Validate
--------

This section describes how to interact with the various validation endpoints.

On validation failure, a response will be sent on the following format ::

  {
    "description": "Invalid phone number",
    "error": true,
    "error_key": "V_INVALID_ADDRESS_PHONE",
    "status": 400,
    "value": "1111111"
  }

*  ``error_key`` is a key used to uniquely identify the validation error that occurred.
*  ``description`` is a human-readable description of the error
*  ``error`` is always ``true``
*  ``status`` will indicate the HTTP status code which was returned
*  ``value`` will be the value that failed validation

Furthermore, a variable amount of additional parameters will be returned
depending on the error, containing helpful information describing the
expected result

All the possible validation errors that can occur can be seen at :ref:`errorcodes`.

.. automodule:: mora.service.validate


.. qrefflask:: mora.app:create_app()
   :blueprints: validate
   :order: path

.. autoflask:: mora.app:create_app()
   :include-empty-docstring:
   :order: path
   :blueprints: validate

.. Indices and tables
   ==================

   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`
