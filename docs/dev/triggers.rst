Customization and Triggers
==========================

In order to keep customizations out of the main code base os2mo includes 
a 'customer' directory meant to be used as a mount point for importing
customer specific code into the os2mo runtime.

The intended way of customizing code is through the use of triggers.

Functions can be decorated so they fired at different stages in the request life cycle. 

 * ``ON_BEFORE``: this is typically fired after the request's prepare phase
 * ``ON_AFTER``: this is typically fired after the request's commit phase

The customer module
-------------------

A directory placed on the host machine (outside the container / module path) is mounted over the os2mo/backend/mora/customer

In order to facilitate tests of customer modules, imports in this code should be absolute, so that the mapping module is imported like: ::

    from os2mo.backend.mora import mapping

rather than using the short form: ::

    from .. import mapping

The ``__init__.py`` in the customer module directory must import any code that is needed for the customizations, and it must all reside in this directory as the directory is unaware of its physical surroundings once it is mounted inside the OS2mo container.

Once mounted this module has access to any and all code inside the customer module as well as any code in OS2mo's python environment including os2mo itself.

The Trigger function
--------------------

A trigger function will receive only one argument, the trigger_dict, which is a dictionary with information about the event

ON_BEFORE
^^^^^^^^^

An ``ON_BEFORE`` trigger_dict will typically contain at least these items: ::

    {
        'event_type': Trigger.Event.ON_BEFORE,
        'request': {}, # the object that was received by the handler
        'request_type': RequestType.EDIT,
        'uuid': '' # the uuid of the object being edited
    }


ON_AFTER
^^^^^^^^

For an ``ON_AFTER`` trigger_dict an additional key is added - the result: ::

    {
        'event_type': Trigger.Event.ON_AFTER,
        'request': {}, # the object that was received by the handler
        'request_type': RequestType.EDIT,
        'uuid': '' # the uuid of the object being manipulated
        'result': '' # the result that is to be sent back to the client
    }

A customer module example
-------------------------

An example implementation of a supermounted directory: ::

    customer
    ├── __init__.py
    ├── employee.py
    └── org_unit.py

The __init__.py file: ::

    from . import org_unit
    from . import employee

The org_unit.py looks like this: ::

    from os2mo.backend.mora.triggers import Trigger
    from os2mo.backend.mora.mapping import ORG_UNIT
    from os2mo.backend.mora.service.handlers import RequestType

    @Trigger.on(ORG_UNIT, RequestType.CREATE, Trigger.Event.ON_BEFORE)
    def ou_before_create(trigger_dict):
        pass

    @Trigger.on(ORG_UNIT, RequestType.CREATE, Trigger.Event.ON_AFTER)
    def ou_after_create(trigger_dict):
        pass

The employee.py looks like this: ::

    from os2mo.backend.mora.triggers import Trigger
    from os2mo.backend.mora.mapping import EMPLOYEE
    from os2mo.backend.mora.service.handlers import RequestType

    @Trigger.on(EMPLOYEE, RequestType.EDIT, Trigger.Event.ON_BEFORE)
    def e_before_edit(trigger_dict):
        pass

    @Trigger.on(EMPLOYEE, RequestType.DELETE, Trigger.Event.ON_AFTER)
    def e_after_delete(trigger_dict):
        pass
