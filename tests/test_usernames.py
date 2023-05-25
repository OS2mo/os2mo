# -*- coding: utf-8 -*-
from collections.abc import Iterator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from fastramqpi.context import Context
from ramodels.mo import Employee

from .conftest import read_mapping
from mo_ldap_import_export.exceptions import IncorrectMapping
from mo_ldap_import_export.usernames import AlleroedUserNameGenerator
from mo_ldap_import_export.usernames import UserNameGenerator


@pytest.fixture
def dataloader() -> MagicMock:
    return MagicMock()


@pytest.fixture
def context(dataloader: MagicMock, converter: MagicMock) -> Context:

    mapping = {
        "mo_to_ldap": {"Employee": {"objectClass": "user"}},
        "username_generator": {
            "char_replacement": {"ø": "oe", "æ": "ae", "å": "aa"},
            "forbidden_usernames": ["holes", "hater"],
            "combinations_to_try": ["F123L", "F12LL", "F1LLL", "FLLLL", "FLLLLX"],
        },
    }

    settings_mock = MagicMock()
    settings_mock.ldap_search_base = "DC=bar"
    settings_mock.ldap_ou_for_new_users = ""

    context: Context = {
        "user_context": {
            "mapping": mapping,
            "settings": settings_mock,
            "dataloader": dataloader,
            "converter": converter,
        }
    }

    return context


@pytest.fixture
def existing_usernames() -> list:
    return ["nj", "ngc"]


@pytest.fixture
def existing_common_names() -> list:
    return ["Nick Janssen", "Nick Janssen_2"]


@pytest.fixture
def existing_usernames_ldap(existing_usernames, existing_common_names) -> list:

    existing_usernames_ldap = [
        {"attributes": {"cn": cn, "sAMAccountName": sam}}
        for cn, sam in zip(existing_common_names, existing_usernames)
    ]
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


@pytest.fixture
def alleroed_username_generator(
    context: Context, existing_usernames_ldap: list
) -> Iterator[AlleroedUserNameGenerator]:

    context["user_context"]["mapping"] = read_mapping("alleroed.json")

    with patch(
        "mo_ldap_import_export.usernames.paged_search",
        return_value=existing_usernames_ldap,
    ):
        yield AlleroedUserNameGenerator(context)


def test_get_existing_usernames(
    username_generator: UserNameGenerator,
    existing_usernames: list,
    existing_common_names: list,
):
    result = username_generator.get_existing_values("sAMAccountName")
    assert result == existing_usernames

    result = username_generator.get_existing_values("cn")
    assert result == [cn.lower() for cn in existing_common_names]


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
        "mo_ldap_import_export.usernames.UserNameGenerator.get_existing_values",
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


def test_create_common_name(username_generator: UserNameGenerator):

    # Regular case
    common_name = username_generator._create_common_name(["Nick", "Johnson"])
    assert common_name == "Nick Johnson"

    # When 'Nick Janssen' already exists and so does 'Nick Janssen_2'
    common_name = username_generator._create_common_name(["Nick", "Janssen"])
    assert common_name == "Nick Janssen_3"

    # Middle names are not used
    common_name = username_generator._create_common_name(
        ["Nick", "Gerardus", "Cornelis", "Johnson"]
    )
    assert common_name == "Nick Gerardus Cornelis Johnson"

    # Users without a last name are supported
    common_name = username_generator._create_common_name(["Nick", ""])
    assert common_name == "Nick"

    # Nick_1 until Nick_2000 exists - we cannot generate a username
    with patch(
        "mo_ldap_import_export.usernames.UserNameGenerator.get_existing_values",
        return_value=["nick"] + [f"nick_{d}" for d in range(2000)],
    ):
        with pytest.raises(RuntimeError):
            username_generator._create_common_name(["Nick", ""])

    # If a name is over 64 characters, a middle name is removed.
    common_name = username_generator._create_common_name(
        ["Nick", "Gerardus", "Cornelis", "long name" * 20, "Johnson"]
    )
    assert common_name == "Nick Gerardus Cornelis Johnson"

    # If the name is still over 64 characters, another middle name is removed.
    common_name = username_generator._create_common_name(
        ["Nick", "Gerardus", "Cornelis", "long name" * 20, "Hansen", "Johnson"]
    )
    assert common_name == "Nick Gerardus Cornelis Johnson"

    # In the rare case that someone has a first or last name with over 64 characters,
    # we cut off characters from his name
    # Because AD does not allow common names with more than 64 characters
    common_name = username_generator._create_common_name(["Nick" * 40, "Johnson"])
    assert common_name == ("Nick" * 40)[:60]

    common_name = username_generator._create_common_name(["Nick", "Johnson" * 40])
    assert common_name == ("Nick" + " " + "Johnson" * 40)[:60]

    common_name = username_generator._create_common_name(
        ["Nick", "Gerardus", "Cornelis", "Johnson" * 40]
    )
    assert common_name == ("Nick" + " " + "Johnson" * 40)[:60]


def test_generate_dn(username_generator: UserNameGenerator):
    employee = Employee(givenname="Patrick", surname="Bateman")
    dn = username_generator.generate_dn(employee)
    assert dn == "CN=Patrick Bateman,DC=bar"


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

    # Test with a user without a last name
    name = ["Nick", ""]
    combi = "FFFL"
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


def test_alleroed_username_generator(
    alleroed_username_generator: AlleroedUserNameGenerator,
):

    generated_usernames = []
    alleroed_username_generator.get_existing_values = MagicMock()  # type: ignore
    alleroed_username_generator.get_existing_values.return_value = []

    def generate_username(name):
        username = alleroed_username_generator.generate_username(name)

        generated_usernames.append(username)
        alleroed_username_generator.get_existing_values.return_value = (  # type: ignore
            generated_usernames
        )

        # Print human readable output to send to Alleroed
        full_name = " ".join(name)
        print(f"{full_name} -> '{username}'")

        return username

    assert generate_username(["Lars", "Løkke", "Rasmussen"]) == "llkk"
    assert generate_username(["Lone", "Løkke", "Rasmussen"]) == "llkr"
    assert generate_username(["Lærke", "Løkke", "Rasmussen"]) == "llrs"
    assert generate_username(["Leo", "Løkke", "Rasmussen"]) == "lrsm"
    assert generate_username(["Lukas", "Løkke", "Rasmussen"]) == "llkkr"
    assert generate_username(["Liam", "Løkke", "Rasmussen"]) == "llkrs"
    assert generate_username(["Ludvig", "Løkke", "Rasmussen"]) == "llrsm"
    assert generate_username(["Laurits", "Løkke", "Rasmussen"]) == "lrsms"
    assert generate_username(["Loki", "Løkke", "Rasmussen"]) == "llr"
    assert generate_username(["Lasse", "Løkke", "Rasmussen"]) == "lrs"
    assert generate_username(["Leonardo", "Løkke", "Rasmussen"]) == "lr"
    assert generate_username(["Laus", "Løkke", "Rasmussen"]) == "lr2"

    assert (
        generate_username(["Margrethe", "Alexandrine", "borhildur", "Ingrid"]) == "mlxn"
    )

    assert generate_username(["Mia", "Alexandrine", "borhildur", "Ingrid"]) == "mlxb"
    assert generate_username(["Mike", "Alexandrine", "borhildur", "Ingrid"]) == "mlbr"
    assert generate_username(["Max", "Alexandrine", "borhildur", "Ingrid"]) == "mbrh"
    assert generate_username(["Mick", "Alexandrine", "borhildur", "Ingrid"]) == "mlbn"
    assert generate_username(["Mads", "Alexandrine", "borhildur", "Ingrid"]) == "mbrn"

    assert generate_username(["Bruce", "Lee"]) == "bl"
    assert generate_username(["Boris", "Lee"]) == "bl2"
    assert generate_username(["Benjamin", "Lee"]) == "bl3"

    assert generate_username(["Bruce", ""]) == "bruc"


def test_alleroed_dn_generator(alleroed_username_generator: AlleroedUserNameGenerator):

    employee = Employee(givenname="Patrick", surname="Bateman")
    dn = alleroed_username_generator.generate_dn(employee)
    assert dn == "CN=Patrick Bateman,DC=bar"
