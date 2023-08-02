# -*- coding: utf-8 -*-
import os
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
            "forbidden_usernames_path": os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "mo_ldap_import_export",
                "mappings",
                "forbidden_usernames",
            ),
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
def existing_user_principal_names() -> list:
    return ["nj@magenta.dk", "ngc2@magenta.dk"]


@pytest.fixture
def existing_usernames_ldap(
    existing_usernames, existing_common_names, existing_user_principal_names
) -> list:

    existing_usernames_ldap = [
        {"attributes": {"cn": cn, "sAMAccountName": sam, "userPrincipalName": up}}
        for cn, sam, up in zip(
            existing_common_names, existing_usernames, existing_user_principal_names
        )
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
    result = username_generator.get_existing_values(["sAMAccountName", "cn"])
    assert result["sAMAccountName"] == existing_usernames
    assert result["cn"] == [cn.lower() for cn in existing_common_names]


def test_create_username(username_generator: UserNameGenerator):
    # Regular user
    username = username_generator._create_username(["Nick", "Janssen"], [])
    assert username == "njans"

    # User with a funny character
    username = username_generator._create_username(["Nick", "Jænssen"], [])
    assert username == "njaen"

    # User with a funny character which is not in the character replacement mapping
    username = username_generator._create_username(["N1ck", "Janssen"], [])
    assert username == "njans"

    # User with a middle name
    username = username_generator._create_username(["Nick", "Gerardus", "Janssen"], [])
    assert username == "ngjan"

    # User with two middle names
    username = username_generator._create_username(
        ["Nick", "Gerardus", "Cornelis", "Janssen"], []
    )
    assert username == "ngcja"

    # User with three middle names
    username = username_generator._create_username(
        ["Nick", "Gerardus", "Cornelis", "Optimus", "Janssen"], []
    )
    assert username == "ngcoj"

    # User with 4 middle names (only the first three are used)
    username = username_generator._create_username(
        ["Nick", "Gerardus", "Cornelis", "Optimus", "Prime", "Janssen"], []
    )
    assert username == "ngcoj"

    # Simulate case where 'njans' is taken
    username = username_generator._create_username(["Nick", "Janssen"], ["njans"])
    assert username == "njans2"

    # Simulate a case which fits none of the models (last name is too short)
    with pytest.raises(RuntimeError):
        username = username_generator._create_username(["Nick", "Ja"], [])

    # Simulate a case where a forbidden username is generated
    username = username_generator._create_username(
        ["Harry", "Alexander", "Terpstra"], []
    )
    assert username != "hater"
    assert username == "hterp"


def test_create_common_name(username_generator: UserNameGenerator):

    # Regular case
    common_name = username_generator._create_common_name(["Nick", "Johnson"], [])
    assert common_name == "Nick Johnson"

    # When 'Nick Janssen' already exists and so does 'Nick Janssen_2'
    common_name = username_generator._create_common_name(
        ["Nick", "Janssen"], ["nick janssen", "nick janssen_2"]
    )
    assert common_name == "Nick Janssen_3"

    # Middle names are not used
    common_name = username_generator._create_common_name(
        ["Nick", "Gerardus", "Cornelis", "Johnson"], []
    )
    assert common_name == "Nick Gerardus Cornelis Johnson"

    # Users without a last name are supported
    common_name = username_generator._create_common_name(["Nick", ""], [])
    assert common_name == "Nick"

    # Nick_1 until Nick_2000 exists - we cannot generate a username
    with pytest.raises(RuntimeError):
        username_generator._create_common_name(
            ["Nick", ""], ["nick"] + [f"nick_{d}" for d in range(2000)]
        )

    # If a name is over 64 characters, a middle name is removed.
    common_name = username_generator._create_common_name(
        ["Nick", "Gerardus", "Cornelis", "long name" * 20, "Johnson"], []
    )
    assert common_name == "Nick Gerardus Cornelis Johnson"

    # If the name is still over 64 characters, another middle name is removed.
    common_name = username_generator._create_common_name(
        ["Nick", "Gerardus", "Cornelis", "long name" * 20, "Hansen", "Johnson"], []
    )
    assert common_name == "Nick Gerardus Cornelis Johnson"

    # In the rare case that someone has a first or last name with over 64 characters,
    # we cut off characters from his name
    # Because AD does not allow common names with more than 64 characters
    common_name = username_generator._create_common_name(["Nick" * 40, "Johnson"], [])
    assert common_name == ("Nick" * 40)[:60]

    common_name = username_generator._create_common_name(["Nick", "Johnson" * 40], [])
    assert common_name == ("Nick" + " " + "Johnson" * 40)[:60]

    common_name = username_generator._create_common_name(
        ["Nick", "Gerardus", "Cornelis", "Johnson" * 40], []
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

    alleroed_username_generator.forbidden_usernames = []
    existing_names: list[str] = []
    expected_usernames = iter(
        [
            "llkk",
            "llkr",
            "llrs",
            "lrsm",
            "llkkr",
            "llkrs",
            "llrsm",
            "lrsms",
            "llr",
            "lrs",
            "lr",
            "lr2",
            "mlxn",
            "mlxb",
            "mlbr",
            "mbrh",
            "mlbn",
            "mbrn",
            "bl",
            "bl2",
            "bl3",
            "bruc",
        ]
    )

    for name in [
        ["Lars", "Løkke", "Rasmussen"],
        ["Lone", "Løkke", "Rasmussen"],
        ["Lærke", "Løkke", "Rasmussen"],
        ["Leo", "Løkke", "Rasmussen"],
        ["Lukas", "Løkke", "Rasmussen"],
        ["Liam", "Løkke", "Rasmussen"],
        ["Ludvig", "Løkke", "Rasmussen"],
        ["Laurits", "Løkke", "Rasmussen"],
        ["Loki", "Løkke", "Rasmussen"],
        ["Lasse", "Løkke", "Rasmussen"],
        ["Leonardo", "Løkke", "Rasmussen"],
        ["Laus", "Løkke", "Rasmussen"],
        ["Margrethe", "Alexandrine", "borhildur", "Ingrid"],
        ["Mia", "Alexandrine", "borhildur", "Ingrid"],
        ["Mike", "Alexandrine", "borhildur", "Ingrid"],
        ["Max", "Alexandrine", "borhildur", "Ingrid"],
        ["Mick", "Alexandrine", "borhildur", "Ingrid"],
        ["Mads", "Alexandrine", "borhildur", "Ingrid"],
        ["Bruce", "Lee"],
        ["Boris", "Lee"],
        ["Benjamin", "Lee"],
        ["Bruce", ""],
    ]:
        username = alleroed_username_generator.generate_username(name, existing_names)
        assert username == next(expected_usernames)
        existing_names.append(username)

        # Print human readable output to send to Alleroed
        full_name = " ".join(name)
        print(f"{full_name} -> '{username}'")


def test_alleroed_dn_generator(alleroed_username_generator: AlleroedUserNameGenerator):

    employee = Employee(givenname="Patrick", surname="Bateman")
    dn = alleroed_username_generator.generate_dn(employee)
    assert dn == "CN=Patrick Bateman,DC=bar"


def test_read_usernames_from_text_file(username_generator: UserNameGenerator):

    usernames = username_generator.read_usernames_from_text_file("itsm_brugere.csv")
    assert "anls" in usernames

    usernames = username_generator.read_usernames_from_text_file(
        "CURA-76507-total-brugerliste-fhir.txt"
    )
    assert "abrn" in usernames


def test_alleroed_username_generator_forbidden_names_from_files(
    alleroed_username_generator: AlleroedUserNameGenerator,
):

    # Try to generate a name that is in CURA-76507-total-brugerliste-fhir.txt
    name = ["Anders", "Broon"]
    username = alleroed_username_generator.generate_username(name, [])
    assert username != "abrn"

    # Try to generate a name that is in itsm_brugere.csv
    name = ["Anders", "Nolus"]
    username = alleroed_username_generator.generate_username(name, [])
    assert username != "anls"

    # Now clean the list of forbidden usernames and try again
    alleroed_username_generator.forbidden_usernames = []

    name = ["Anders", "Broon"]
    username = alleroed_username_generator.generate_username(name, [])
    assert username == "abrn"

    name = ["Anders", "Nolus"]
    username = alleroed_username_generator.generate_username(name, [])
    assert username == "anls"


def test_is_filename(username_generator: UserNameGenerator):

    assert username_generator.is_filename("foo.txt") is True
    assert username_generator.is_filename("foo.TXT") is True
    assert username_generator.is_filename("foo.csv") is True
    assert username_generator.is_filename("foo.CSV") is True
    assert username_generator.is_filename("foo") is False
