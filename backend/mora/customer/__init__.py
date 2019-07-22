"""
This is a placeholder directory, which will act as a mount point for customer specific code

A directory placed on the host machine (outside the container / module path)will override this file ensuring that the OS2mo code running across all customers is the same while allowing customizations outside the OS2mo repository

In order to facilitate tests of customer modules, imports should be absolute, so that the mapping module is imported like:

    from os2mo.backend.mora import mapping

rather than using the short form:

    from .. import mapping

Thus testing a customer module can be prepared by simply patching the mora module in a test

The __init__.py file must import any code that is needed for the customizations, and it must all reside in this directory as the directory is unaware of its physical surroundings once it is mounted inside the OS2mo container.

Once mounted this module has access to any and all code inside the customer module as well as any code in OS2mo's python environment including os2mo itself.


An example implementation of a supermounted directory:

    customer
    ├── __init__.py
    ├── employee.py
    └── org_unit.py

The __init__.py file:

    from . import org_unit
    from . import employee

The org_unit.py looks like this:

    from os2mo.backend.mora.triggers import Trigger
    from os2mo.backend.mora.mapping import (
        ORG_UNIT,
        ON_BEFORE,
        ON_AFTER,
    )
    from os2mo.backend.mora.service.handlers import RequestType

    @Trigger.on(ORG_UNIT, RequestType.CREATE, ON_BEFORE)
    def ou_before_create(trigger_dict):
        pass

    @Trigger.on(ORG_UNIT, RequestType.CREATE, ON_AFTER)
    def ou_after_create(trigger_dict):
        pass

The employee.py looks like this:

    from os2mo.backend.mora.triggers import Trigger
    from os2mo.backend.mora.mapping import (
        EMPLOYEE,
        ON_BEFORE,
        ON_AFTER,
    )
    from os2mo.backend.mora.service.handlers import RequestType

    @Trigger.on(EMPLOYEE, RequestType.EDIT, ON_BEFORE)
    def e_before_edit(trigger_dict):
        pass

    @Trigger.on(EMPLOYEE, RequestType.DELETE, ON_AFTER)
    def e_after_delete(trigger_dict):
        pass


"""
