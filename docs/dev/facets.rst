Facets
======

Facets serve as a grouping of different classes.
Within the data models used in OS2MO, model fields corresponding to a facet
name is expected to contain a reference to a class contained in that facet.
E.g. the field ``responsibility`` in the ``manager`` data model, contains a
reference to a class contained in the ``responsibility`` facet.

Similarly, when creating new relations or objects in the UI, the dropdown for
selecting ``responsibility`` will contain every class from the
``responsibility`` facet.

The exception to this general rule, is the field ``address_type`` found in
various data models. For this field, various address type facets exist
depending on which context the field is used in.
E.g. ``address_type`` associated with ``manager`` objects, should contain a
class from the ``manager_address_type`` facet. The ``address_type`` classes
relevant in multiple contexts should be related to multiple facets, as
opposed to duplicating the classes for each facet.

The system currently works with the following facets:

+---------------------------+-----------------------------------------------------------+
| Name                      | Description                                               |
+===========================+===========================================================+
| ``org_unit_address_type`` | Address types applicable for organisational units         |
+---------------------------+-----------------------------------------------------------+
| ``employee_address_type`` | Address types applicable for employees                    |
+---------------------------+-----------------------------------------------------------+
| ``manager_address_type``  | Address types applicable for managers                     |
+---------------------------+-----------------------------------------------------------+
| ``address_property``      | Properties for addresses, e.g. public or secret addresses |
+---------------------------+-----------------------------------------------------------+
| ``job_title``             | Job titles                                                |
+---------------------------+-----------------------------------------------------------+
| ``org_unit_type``         | Types of organisational units                             |
+---------------------------+-----------------------------------------------------------+
| ``engagement_type``       | Types of engagements                                      |
+---------------------------+-----------------------------------------------------------+
| ``association_type``      | Types of associations                                     |
+---------------------------+-----------------------------------------------------------+
| ``role_type``             | Types of roles                                            |
+---------------------------+-----------------------------------------------------------+
| ``leave_type``            | Types of leave, e.g. maternity leave                      |
+---------------------------+-----------------------------------------------------------+
| ``manager_type``          | Types of managers                                         |
+---------------------------+-----------------------------------------------------------+
| ``responsibility``        | Responsibilities for managers                             |
+---------------------------+-----------------------------------------------------------+
| ``manager_level``         | Levels for managers                                       |
+---------------------------+-----------------------------------------------------------+
