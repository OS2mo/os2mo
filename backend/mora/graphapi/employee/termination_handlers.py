from mora import mapping


def terminate_employee_engagments(termination_obj: dict):
    pass


def terminate_employee_addresses():
    pass


def terminate_employee_roles():
    pass


def terminate_employee_it():
    pass


def terminate_employee_it_relations():
    pass


def terminate_employee_leave_of_absence():
    pass


def terminate_employee_leader():
    pass


HANDLERS_BY_FUNCTION_KEY = {
    mapping.ADDRESS_KEY: None,
    mapping.ITSYSTEM_KEY: None,
    mapping.ASSOCIATION_KEY: None,
    mapping.ENGAGEMENT_KEY: terminate_employee_engagments,
    mapping.ENGAGEMENT_ASSOCIATION_KEY: None,
    mapping.KLE_KEY: None,
    mapping.LEAVE_KEY: None,
    mapping.MANAGER_KEY: None,
    mapping.OWNER_KEY: None,
    mapping.RELATED_UNIT_KEY: None,
    mapping.ROLE_KEY: None,
}
