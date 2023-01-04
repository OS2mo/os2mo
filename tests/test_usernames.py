# -*- coding: utf-8 -*-
from collections.abc import Iterator
from unittest.mock import MagicMock
from unittest.mock import patch
from unittest.mock import PropertyMock

import pytest
from fastramqpi.context import Context
from ramodels.mo import Employee

from mo_ldap_import_export.exceptions import IncorrectMapping
from mo_ldap_import_export.usernames import UserNameGenerator


@pytest.fixture
def context() -> Context:

    mapping = {
        "mo_to_ldap": {"Employee": {"objectClass": "user"}},
        "username_generator": {
            "char_replacement": {"ø": "oe", "æ": "ae", "å": "aa"},
            "forbidden_usernames": ["holes", "hater"],
            "combinations_to_try": ["F123L", "F12LL", "F1LLL", "FLLLL", "FLLLLX"],
        },
    }

    settings_mock = MagicMock()
    settings_mock.ldap_organizational_unit = "OU=foo"
    settings_mock.ldap_search_base = "DC=bar"

    context: Context = {
        "user_context": {
            "mapping": mapping,
            "settings": settings_mock,
        }
    }

    return context


@pytest.fixture
def existing_usernames() -> list:
    return ["nj", "ngc"]


@pytest.fixture
def existing_usernames_ldap(existing_usernames) -> list:

    existing_usernames_ldap = [{"attributes": {"cn": e}} for e in existing_usernames]
    return existing_usernames_ldap


@pytest.fixture
def username_generator(
    context: Context, existing_usernames_ldap: list
) -> Iterator[UserNameGenerator]:

    with patch(
        "mo_ldap_import_export.usernames.paged_search",
        return_value=existing_usernames_ldap,
    ):
        yield UserNameGenerator(context)


def test_get_existing_usernames(
    username_generator: UserNameGenerator,
    existing_usernames: list,
):
    result = username_generator.existing_usernames
    assert result == existing_usernames


def test_create_username(username_generator: UserNameGenerator):
    # Regular user
    username = username_generator._create_username(["Nick", "Janssen"])
    assert username == "njans"

    # User with a funny character
    username = username_generator._create_username(["Nick", "Jænssen"])
    assert username == "njaen"

    # User with a funny character which is not in the character replacement mapping
    username = username_generator._create_username(["N1ck", "Janssen"])
    assert username == "njans"

    # User with a middle name
    username = username_generator._create_username(["Nick", "Gerardus", "Janssen"])
    assert username == "ngjan"

    # User with two middle names
    username = username_generator._create_username(
        ["Nick", "Gerardus", "Cornelis", "Janssen"]
    )
    assert username == "ngcja"

    # User with three middle names
    username = username_generator._create_username(
        ["Nick", "Gerardus", "Cornelis", "Optimus", "Janssen"]
    )
    assert username == "ngcoj"

    # User with 4 middle names (only the first three are used)
    username = username_generator._create_username(
        ["Nick", "Gerardus", "Cornelis", "Optimus", "Prime", "Janssen"]
    )
    assert username == "ngcoj"

    # Simulate case where 'njans' is taken
    with patch(
        "mo_ldap_import_export.usernames.UserNameGenerator.existing_usernames",
        new_callable=PropertyMock,
        return_value=["njans"],
    ):
        username = username_generator._create_username(["Nick", "Janssen"])
        assert username == "njans2"

    # Simulate a case which fits none of the models (last name is too short)
    with pytest.raises(RuntimeError):
        username = username_generator._create_username(["Nick", "Ja"])

    # Simulate a case where a forbidden username is generated
    username = username_generator._create_username(["Harry", "Alexander", "Terpstra"])
    assert username != "hater"
    assert username == "hterp"


def test_generate_dn(username_generator: UserNameGenerator):
    employee = Employee(givenname="Nick Gerardus Cornelis", surname="Janssen")
    dn = username_generator.generate_dn(employee)
    assert dn == "CN=ngcja,OU=foo,DC=bar"


def test_create_from_combi(username_generator: UserNameGenerator):

    # Test with a combi that starts with an 'X'
    name = ["Nick", "Janssen"]
    combi = "XFL"
    username = username_generator._create_from_combi(name, combi)
    assert username == "Xnj"

    # Test with a combi that expects 5 characters for the first name
    name = ["Nick", "Janssen"]
    combi = "FFFFFL"
    username = username_generator._create_from_combi(name, combi)
    assert username is None


def test_check_json_inputs(username_generator: UserNameGenerator):
    username_generator.mapping = {}
    with pytest.raises(IncorrectMapping, match="'username_generator' key not present"):
        username_generator.check_json_inputs()


def test_check_combinations_to_try(username_generator: UserNameGenerator):
    username_generator.mapping = {"username_generator": {}}
    with pytest.raises(IncorrectMapping, match="'combinations_to_try' key not present"):
        username_generator._check_combinations_to_try()

    username_generator.mapping = {
        "username_generator": {"combinations_to_try": ["GAK"]}
    }
    with pytest.raises(IncorrectMapping, match="Incorrect combination"):
        username_generator._check_combinations_to_try()


def test_check_forbidden_usernames(username_generator: UserNameGenerator):
    username_generator.mapping = {"username_generator": {}}
    with pytest.raises(IncorrectMapping, match="'forbidden_usernames' key not present"):
        username_generator._check_forbidden_usernames()

    username_generator.mapping = {
        "username_generator": {"forbidden_usernames": ["foo", 23]}
    }
    with pytest.raises(IncorrectMapping, match="Incorrect username"):
        username_generator._check_forbidden_usernames()


def test_check_check_char_replacement(username_generator: UserNameGenerator):
    username_generator.mapping = {"username_generator": {}}
    with pytest.raises(IncorrectMapping, match="'char_replacement' key not present"):
        username_generator._check_char_replacement()

    username_generator.mapping = {"username_generator": {"char_replacement": [1, 2, 3]}}
    with pytest.raises(IncorrectMapping, match="entry must be a <class 'dict'>"):
        username_generator._check_char_replacement()
