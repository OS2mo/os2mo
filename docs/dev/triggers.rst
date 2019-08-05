Customization and Triggers
==========================

In order to keep customizations out of the main code base os2mo includes 
a 'customer' directory meant to be used as a mount point for importing
customer specific code into the os2mo runtime.

The intended way of customizing code is through the use of triggers.

Functions can be decorated so they fired at different stages in the request life cycle. 

 * ``ON_BEFORE``: this is typically fired after the request's prepare phase
 * ``ON_AFTER``: this is typically fired after the request's commit phase

Triggers deployed in OS2mo
--------------------------

OS2mo itself uses triggers for internal purposes.

All OS2mo internal triggers should be defined beneath in scripts inside the mora/triggers module and then these scripts must be imported by the file ``mora_triggers.py`` in order for the triggers to be activated. See the ``amqp_trigger.py`` in that module for an example.


The customer module
-------------------

A directory placed on the host machine (outside the container / module path) is mounted over the os2mo/backend/mora/customer

Development and test should be performed with the directory mounted in, so relative imports work: ::

    from ..triggers import Trigger

The ``__init__.py`` in the customer module directory must import any code that is needed for the customizations, and it must all reside in this directory or be available in the python environment as the directory is unaware of its physical surroundings once it is mounted inside the OS2mo container.

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
        'role_type': '' # role_type of the request
        'uuid': '' # the uuid of the object being edited

    }


ON_AFTER
^^^^^^^^

For an ``ON_AFTER`` trigger_dict an additional key is added - the result: ::

    {
        'event_type': Trigger.Event.ON_AFTER,
        'request': {}, # the object that was received by the handler
        'request_type': RequestType.EDIT,
        'result': '' # the result that is to be sent back to the client
        'role_type': '' # role_type of the request
        'uuid': '' # the uuid of the object being manipulated
    }

Triggerless mode
----------------

It can be reasonable to turn off trigger-functionality when for example loading a complete data-set into OS2mo. In case You want that, specify the flag: ``triggerless`` in the request like: ``http://example.com?triggerless=1``

Using triggerless requests also disables amqp-messages.


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

    import logging
    from ..triggers import Trigger
    from ..mapping import ORG_UNIT
    from ..service.handlers import RequestType

    logger = logging.getLogger("org_unit_trigger")

    @Trigger.on(ORG_UNIT, RequestType.CREATE, Trigger.Event.ON_BEFORE)
    def ou_before_create(trigger_dict):
        logger.warning(trigger_dict)

    @Trigger.on(ORG_UNIT, RequestType.CREATE, Trigger.Event.ON_AFTER)
    def ou_after_create(trigger_dict):
        logger.warning(trigger_dict)

The empoyee.py file looks like this: ::

    import logging
    from ..triggers import Trigger
    from ..mapping import EMPLOYEE
    from ..service.handlers import RequestType

    logger = logging.getLogger("employee_trigger")

    @Trigger.on(EMPLOYEE, RequestType.EDIT, Trigger.Event.ON_BEFORE)
    def e_before_edit(trigger_dict):
        logger.warning(trigger_dict)

    @Trigger.on(EMPLOYEE, RequestType.TERMINATE, Trigger.Event.ON_AFTER)
    def e_after_delete(trigger_dict):
        logger.warning(trigger_dict)
