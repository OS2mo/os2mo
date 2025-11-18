# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from unittest.mock import ANY
from uuid import UUID

import pytest

from ..conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_address_resolver_response_fields(
    graphapi_post: GraphAPIPost,
    create_person: Callable[..., UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
) -> None:
    employee_address_type_facet = create_facet(
        {
            "user_key": "employee_address_type",
            "validity": {"from": "1970-01-01"},
        }
    )
    post_address_class = create_class(
        {
            "user_key": "AdressePostEmployee",
            "scope": "DAR",
            "name": "Postadresse",
            "facet_uuid": str(employee_address_type_facet),
            "validity": {"from": "1970-01-01"},
        }
    )

    person_uuid = create_person()
    value = "1a6da4cb-e2b4-40a3-b9c0-ff4f2f5fba97"

    create_address_mutation = """
    mutation CreateAddress($input: AddressCreateInput!) {
      address_create(input: $input) {
        uuid
      }
    }
    """
    input = {
        "address_type": str(post_address_class),
        "value": value,
        "person": str(person_uuid),
        "validity": {"from": "2000-01-01T00:00:00Z"},
    }
    response = graphapi_post(create_address_mutation, variables={"input": input})
    assert response.errors is None
    assert response.data is not None
    address_uuid = response.data["address_create"]["uuid"]

    query = """
        query ResponseAddresses {
          addresses {
            objects {
              current {
                uuid
                address_type_response {
                  uuid
                  current {
                    name
                    validity {
                      from
                      to
                    }
                  }
                }
                engagement_response {
                  uuid
                }
                ituser_response {
                  uuid
                }
                org_unit_response {
                  uuid
                }
                person_response {
                  uuid
                }
                visibility_response {
                  uuid
                }
              }
            }
          }
        }
    """

    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {
        "addresses": {
            "objects": [
                {
                    "current": {
                        "uuid": address_uuid,
                        "address_type_response": {
                            "uuid": str(post_address_class),
                            "current": {
                                "name": "Postadresse",
                                "validity": {
                                    "from": "1970-01-01T00:00:00+01:00",
                                    "to": None,
                                },
                            },
                        },
                        "engagement_response": None,
                        "ituser_response": None,
                        "org_unit_response": None,
                        "person_response": {"uuid": str(person_uuid)},
                        "visibility_response": {"uuid": ANY},
                    }
                }
            ]
        }
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_address_resolver_response_field_comparison(
    graphapi_post: GraphAPIPost,
    create_person: Callable[..., UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
) -> None:
    employee_address_type_facet = create_facet(
        {
            "user_key": "employee_address_type",
            "validity": {"from": "1970-01-01"},
        }
    )
    post_address_class = create_class(
        {
            "user_key": "AdressePostEmployee",
            "scope": "DAR",
            "name": "Postadresse",
            "facet_uuid": str(employee_address_type_facet),
            "validity": {"from": "1970-01-01"},
        }
    )

    person_uuid = create_person()
    value = "1a6da4cb-e2b4-40a3-b9c0-ff4f2f5fba97"

    create_address_mutation = """
    mutation CreateAddress($input: AddressCreateInput!) {
      address_create(input: $input) {
        uuid
      }
    }
    """
    input = {
        "address_type": str(post_address_class),
        "value": value,
        "person": str(person_uuid),
        "validity": {"from": "2000-01-01T00:00:00Z"},
    }
    response = graphapi_post(create_address_mutation, variables={"input": input})
    assert response.errors is None
    assert response.data is not None
    address_uuid = response.data["address_create"]["uuid"]

    query = """
        query ResponseAddresses {
          addresses {
            objects {
              current {
                uuid
                address_type {
                    name
                    validity {
                      from
                      to
                    }
                }
                address_type_validity {
                    name
                    validity {
                      from
                      to
                    }
                }
                address_type_response {
                  current {
                    name
                    validity {
                      from
                      to
                    }
                  }
                }
              }
            }
          }
        }
    """

    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {
        "addresses": {
            "objects": [
                {
                    "current": {
                        "uuid": address_uuid,
                        "address_type": {
                            "name": "Postadresse",
                            "validity": {
                                "from": "1970-01-01T00:00:00+01:00",
                                "to": None,
                            },
                        },
                        "address_type_validity": {
                            "name": "Postadresse",
                            "validity": {
                                "from": "1970-01-01T00:00:00+01:00",
                                "to": None,
                            },
                        },
                        "address_type_response": {
                            "current": {
                                "name": "Postadresse",
                                "validity": {
                                    "from": "1970-01-01T00:00:00+01:00",
                                    "to": None,
                                },
                            },
                        },
                    }
                }
            ]
        }
    }

    class_update_mutation = """
        mutation ClassUpdate($input: ClassUpdateInput!) {
            class_update(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(
        query=class_update_mutation,
        variables={
            "input": {
                "uuid": str(post_address_class),
                # Old fields
                "user_key": "AdressePostEmployee",
                "scope": "DAR",
                "facet_uuid": str(employee_address_type_facet),
                # New fields
                "name": "New name",
                "validity": {"from": "2010-01-01"},
            }
        },
    )
    assert response.errors is None

    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {
        "addresses": {
            "objects": [
                {
                    "current": {
                        "uuid": address_uuid,
                        "address_type": {
                            "name": "New name",
                            "validity": {
                                "from": "2010-01-01T00:00:00+01:00",
                                "to": None,
                            },
                        },
                        "address_type_validity": {
                            "name": "Postadresse",
                            "validity": {
                                "from": "1970-01-01T00:00:00+01:00",
                                "to": "2009-12-31T00:00:00+01:00",
                            },
                        },
                        "address_type_response": {
                            "current": {
                                "name": "New name",
                                "validity": {
                                    "from": "2010-01-01T00:00:00+01:00",
                                    "to": None,
                                },
                            },
                        },
                    }
                }
            ]
        }
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_address_resolver_response_field_validity(
    graphapi_post: GraphAPIPost,
    create_person: Callable[..., UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
) -> None:
    employee_address_type_facet = create_facet(
        {
            "user_key": "employee_address_type",
            "validity": {"from": "1970-01-01"},
        }
    )
    post_address_class = create_class(
        {
            "user_key": "AdressePostEmployee",
            "scope": "DAR",
            "name": "Postadresse",
            "facet_uuid": str(employee_address_type_facet),
            "validity": {"from": "1970-01-01"},
        }
    )

    person_uuid = create_person()
    value = "1a6da4cb-e2b4-40a3-b9c0-ff4f2f5fba97"

    create_address_mutation = """
    mutation CreateAddress($input: AddressCreateInput!) {
      address_create(input: $input) {
        uuid
      }
    }
    """
    input = {
        "address_type": str(post_address_class),
        "value": value,
        "person": str(person_uuid),
        "validity": {"from": "2000-01-01T00:00:00Z"},
    }
    response = graphapi_post(create_address_mutation, variables={"input": input})
    assert response.errors is None
    assert response.data is not None
    address_uuid = response.data["address_create"]["uuid"]

    query = """
        query ResponseAddresses {
          addresses {
            objects {
              current {
                uuid
                address_type_response {
                  validities(start: null, end: null) {
                    name
                    validity {
                      from
                      to
                    }
                  }
                }
              }
            }
          }
        }
    """

    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {
        "addresses": {
            "objects": [
                {
                    "current": {
                        "uuid": address_uuid,
                        "address_type_response": {
                            "validities": [
                                {
                                    "name": "Postadresse",
                                    "validity": {
                                        "from": "1970-01-01T00:00:00+01:00",
                                        "to": None,
                                    },
                                }
                            ],
                        },
                    }
                }
            ]
        }
    }

    class_update_mutation = """
        mutation ClassUpdate($input: ClassUpdateInput!) {
            class_update(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(
        query=class_update_mutation,
        variables={
            "input": {
                "uuid": str(post_address_class),
                # Old fields
                "user_key": "AdressePostEmployee",
                "scope": "DAR",
                "facet_uuid": str(employee_address_type_facet),
                # New fields
                "name": "New name",
                "validity": {"from": "2010-01-01"},
            }
        },
    )
    assert response.errors is None

    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {
        "addresses": {
            "objects": [
                {
                    "current": {
                        "uuid": address_uuid,
                        "address_type_response": {
                            "validities": [
                                {
                                    "name": "Postadresse",
                                    "validity": {
                                        "from": "1970-01-01T00:00:00+01:00",
                                        "to": "2009-12-31T00:00:00+01:00",
                                    },
                                },
                                {
                                    "name": "New name",
                                    "validity": {
                                        "from": "2010-01-01T00:00:00+01:00",
                                        "to": None,
                                    },
                                },
                            ],
                        },
                    }
                }
            ]
        }
    }
