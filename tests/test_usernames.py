# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from collections.abc import Iterator
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastramqpi.context import Context
from pydantic import ValidationError
from pydantic import parse_obj_as

from mo_ldap_import_export.config import UsernameGeneratorConfig
from mo_ldap_import_export.depends import GraphQLClient
from mo_ldap_import_export.depends import Settings
from mo_ldap_import_export.moapi import MOAPI
from mo_ldap_import_export.models import Employee
from mo_ldap_import_export.usernames import UserNameGenerator
from tests.graphql_mocker import GraphQLMocker


@pytest.fixture
def dataloader() -> MagicMock:
    mock = MagicMock()
    mock.load_all_it_users = AsyncMock()
    mock.ldapapi.add_ldap_object = AsyncMock()
    mock.moapi = AsyncMock()
    return mock


@pytest.fixture
def context(
    minimal_valid_environmental_variables: None,
    monkeypatch: pytest.MonkeyPatch,
    dataloader: MagicMock,
    converter: MagicMock,
) -> Context:
    mapping = {
        "username_generator": {
            "char_replacement": {"ø": "oe", "æ": "ae", "å": "aa"},
            "forbidden_usernames": ["holes", "hater"],
            "combinations_to_try": ["F123L", "F12LL", "F1LLL", "FLLLL", "FLLLLX"],
        },
    }
    monkeypatch.setenv("CONVERSION_MAPPING", json.dumps(mapping))
    monkeypatch.setenv("LDAP_SEARCH_BASE", "DC=bar")
    monkeypatch.setenv("LDAP_DIALECT", "AD")
    monkeypatch.setenv("LDAP_OU_FOR_NEW_USERS", "")

    ldap_connection = AsyncMock()

    context: Context = {
        "user_context": {
            "mapping": mapping,
            "settings": Settings(),
            "dataloader": dataloader,
            "converter": converter,
            "ldap_connection": ldap_connection,
        }
    }

    return context


@pytest.fixture
def existing_usernames() -> set[str]:
    return {"nj", "ngc"}


@pytest.fixture
def existing_common_names() -> set[str]:
    return {"Nick Janssen", "Nick Janssen_2"}


@pytest.fixture
def existing_user_principal_names() -> set[str]:
    return {"nj@magenta.dk", "ngc2@magenta.dk"}


@pytest.fixture
def existing_usernames_ldap(
    existing_usernames: set[str],
    existing_common_names: set[str],
    existing_user_principal_names: set[str],
) -> list:
    existing_usernames_ldap = [
        {"attributes": {"cn": cn, "sAMAccountName": sam, "userPrincipalName": up}}
        for cn, sam, up in zip(
            existing_common_names,
            existing_usernames,
            existing_user_principal_names,
            strict=False,
        )
    ]
    return existing_usernames_ldap


@pytest.fixture
def username_generator(
    minimal_valid_environmental_variables: None,
    context: Context,
    existing_usernames_ldap: list,
) -> Iterator[UserNameGenerator]:
    with patch(
        "mo_ldap_import_export.usernames.paged_search",
        return_value=existing_usernames_ldap,
    ):
        user_context = context["user_context"]
        yield UserNameGenerator(
            Settings(),
            user_context["dataloader"].moapi,
            user_context["ldap_connection"],
        )


@pytest.fixture
def alleroed_username_generator(
    minimal_valid_environmental_variables: None,
    monkeypatch: pytest.MonkeyPatch,
    context: Context,
    existing_usernames_ldap: list,
) -> Iterator[UserNameGenerator]:
    username_generator_config = {
        "objectClass": "UserNameGenerator",
        "char_replacement": {},
        # Note: We need some 'X's in this list. to account for potential duplicates
        # Note2: We need some short combinations in this list, to account for persons with
        # short names.
        #
        # Index:
        # F: First name
        # 1: First middle name
        # 2: Second middle name
        # 3: Third middle name
        # L: Last name
        # X: Number
        #
        # Example1: If combination = "F11LL", 'Hans Jakob Hansen' returns username="hjaha"
        # Example2: If combination = "FFLL", 'Hans Jakob Hansen' returns username="haha"
        "combinations_to_try": [
            # Try to make a username with 4 characters.
            "F111",
            "F112",
            "F122",
            "F222",
            "F223",
            "F233",
            "F333",
            #
            "F11L",
            "F12L",
            "F22L",
            "F23L",
            "F33L",
            #
            "F1LL",
            "F2LL",
            "F3LL",
            #
            "FLLL",
            #
            # If we get to here, we failed to make a username with 4 characters.
            "F111L",
            "F112L",
            "F122L",
            "F222L",
            "F223L",
            "F233L",
            "F333L",
            #
            "F11LL",
            "F12LL",
            "F22LL",
            "F23LL",
            "F33LL",
            #
            "F1LLL",
            "F2LLL",
            "F3LLL",
            #
            "FLLLL",
            #
            # If we get to here, we failed to make a username with only a single
            # character for the first name
            #
            "FF11",
            "FF12",
            "FF22",
            "FF23",
            "FF33",
            "FF1L",
            "FF2L",
            "FF3L",
            "FFLL",
            #
            "FFF1",
            "FFF2",
            "FFF3",
            "FFFL",
            #
            "FFFF",
        ],
        "forbidden_usernames": ["abrn", "anls"],
        "remove_vowels": True,
        "disallow_mo_usernames": True,
    }
    monkeypatch.setenv(
        "CONVERSION_MAPPING",
        json.dumps({"username_generator": username_generator_config}),
    )
    monkeypatch.setenv("LDAP_SEARCH_BASE", "DC=bar")

    with patch(
        "mo_ldap_import_export.usernames.paged_search",
        return_value=existing_usernames_ldap,
    ):
        user_context = context["user_context"]
        yield UserNameGenerator(
            Settings(),
            user_context["dataloader"],
            user_context["ldap_connection"],
        )


async def test_get_existing_usernames(
    username_generator: UserNameGenerator,
    existing_usernames: set[str],
    existing_common_names: set[str],
):
    result = await username_generator.get_existing_values(["sAMAccountName", "cn"])
    assert result["sAMAccountName"] == existing_usernames
    assert result["cn"] == {cn.lower() for cn in existing_common_names}


@pytest.mark.parametrize(
    "names,expected",
    (
        # Regular user
        (["Nick", "Janssen"], "njans"),
        # User with a funny character
        (["Nick", "Jænssen"], "njaen"),
        # User with a funny character which is not in the character replacement mapping
        (["N1ck", "Janssen"], "njans"),
        # User with a middle name
        (["Nick", "Gerardus", "Janssen"], "ngjan"),
        # User with two middle names
        (["Nick", "Gerardus", "Cornelis", "Janssen"], "ngcja"),
        # User with three middle names
        (["Nick", "Gerardus", "Cornelis", "Optimus", "Janssen"], "ngcoj"),
        # User with 4 middle names (only the first three are used)
        (["Nick", "Gerardus", "Cornelis", "Optimus", "Prime", "Janssen"], "ngcoj"),
    ),
)
def test_create_username(
    username_generator: UserNameGenerator, names: list[str], expected: str
) -> None:
    username = username_generator._create_username(names, set())
    assert username == expected


@pytest.mark.parametrize(
    "names,existing,expected",
    (
        # Regular user, but njans is taken
        (["Nick", "Janssen"], {"njans"}, "njans2"),
        # User with a funny character, but njaen is taken
        (["Nick", "Jænssen"], {"njaen"}, "njaen2"),
    ),
)
def test_create_username_taken(
    username_generator: UserNameGenerator,
    names: list[str],
    existing: set[str],
    expected: str,
) -> None:
    username = username_generator._create_username(names, existing)
    assert username == expected


def test_create_username_no_models_fit(username_generator: UserNameGenerator) -> None:
    # Simulate a case which fits none of the models (last name is too short)
    with pytest.raises(RuntimeError):
        username_generator._create_username(["Nick", "Ja"], set())


def test_create_username_forbidden(username_generator: UserNameGenerator) -> None:
    # Simulate a case where a forbidden username is generated
    username = username_generator._create_username(
        ["Harry", "Alexander", "Terpstra"], set()
    )
    assert username != "hater"
    assert username == "hterp"


@pytest.mark.parametrize(
    "names,expected",
    (
        # Regular case
        (["Nick", "Johnson"], "Nick Johnson"),
        # Middle names are not used
        (["Nick", "Gerardus", "Cornelis", "Johnson"], "Nick Gerardus Cornelis Johnson"),
        # Users without a last name are supported
        (["Nick", ""], "Nick"),
        # If a name is over 64 characters, a middle name is removed.
        (
            ["Nick", "Gerardus", "Cornelis", "long name" * 20, "Johnson"],
            "Nick Gerardus Cornelis Johnson",
        ),
        # If the name is still over 64 characters, another middle name is removed.
        (
            ["Nick", "Gerardus", "Cornelis", "long name" * 20, "Hansen", "Johnson"],
            "Nick Gerardus Cornelis Johnson",
        ),
        # In the rare case that someone has a first or last name with over 64 characters,
        # we cut off characters from his name
        # Because AD does not allow common names with more than 64 characters
        (["Nick" * 40, "Johnson"], ("Nick" * 40)[:60]),
        (["Nick", "Johnson" * 40], ("Nick" + " " + "Johnson" * 40)[:60]),
        (
            ["Nick", "Gerardus", "Cornelis", "Johnson" * 40],
            ("Nick" + " " + "Johnson" * 40)[:60],
        ),
    ),
)
def test_create_common_name(
    username_generator: UserNameGenerator, names: list[str], expected: str
) -> None:
    common_name = username_generator._create_common_name(names, set())
    assert common_name == expected


@pytest.mark.parametrize(
    "names,existing,expected",
    (
        # Regular case, but Nick Johnson is taken
        # TODO: Are common names actually case insensitive in LDAP / AD?
        (["Nick", "Johnson"], {"nick johnson"}, "Nick Johnson_2"),
        # Regualr case, but both 'Nick Janssen' and 'Nick Janssen_2' are taken
        (["Nick", "Janssen"], {"nick janssen", "nick janssen_2"}, "Nick Janssen_3"),
    ),
)
def test_create_common_name_taken(
    username_generator: UserNameGenerator,
    names: list[str],
    existing: set[str],
    expected: str,
) -> None:
    common_name = username_generator._create_common_name(names, existing)
    assert common_name == expected


def test_create_common_name_exhausted(username_generator: UserNameGenerator) -> None:
    # Nick_1 until Nick_2000 exists - we cannot generate a username
    with pytest.raises(RuntimeError):
        username_generator._create_common_name(
            ["Nick", ""], {"nick"} | {f"nick_{d}" for d in range(2000)}
        )


async def test_generate_dn(
    monkeypatch: pytest.MonkeyPatch, username_generator: UserNameGenerator
) -> None:
    monkeypatch.setenv("CONVERSION_MAPPING__MO2LDAP", "{}")
    username_generator.settings = Settings()

    employee = Employee(given_name="Patrick", surname="Bateman")
    dn = await username_generator.generate_dn(employee)
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


def test_check_combinations_to_try():
    config = {"combinations_to_try": ["GAK"]}
    with pytest.raises(ValidationError, match="Incorrect combination"):
        parse_obj_as(UsernameGeneratorConfig, config)


async def test_alleroed_username_generator(
    alleroed_username_generator: UserNameGenerator,
) -> None:
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
            "lolk",
            "lalk",
            "lelk",
            "lalr",
            "mlxn",
            "mlxb",
            "mlbr",
            "mbrh",
            "mlbn",
            "mbrn",
            "brul",
            "borl",
            "benl",
            "bruc",
            "dobn",
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
        ["Dorthe", "Baun"],
    ]:
        *firstnames, surname = name
        given_name = " ".join(firstnames)
        employee = Employee(given_name=given_name, surname=surname)

        alleroed_username_generator._get_existing_usernames = AsyncMock()  # type: ignore
        alleroed_username_generator._get_existing_usernames.return_value = (
            existing_names
        )
        username = await alleroed_username_generator.generate_username(employee)
        assert username == next(expected_usernames)
        existing_names.append(username)


async def test_alleroed_dn_generator(
    monkeypatch: pytest.MonkeyPatch,
    alleroed_username_generator: UserNameGenerator,
) -> None:
    monkeypatch.setenv("CONVERSION_MAPPING__MO2LDAP", "{}")
    alleroed_username_generator.settings = Settings()

    employee = Employee(given_name="Patrick", surname="Bateman")
    dn = await alleroed_username_generator.generate_dn(employee)
    assert dn == "CN=Patrick Bateman,DC=bar"


@pytest.mark.parametrize(
    "given_name,surname,forbidden,expected",
    [
        ("Anders", "Broon", [], "abrn"),
        ("Anders", "Broon", ["abrn"], "anbr"),
        ("Anders", "Nolus", [], "anls"),
        ("Anders", "Nolus", ["anls"], "annl"),
    ],
)
async def test_alleroed_username_generator_forbidden_names_from_files(
    alleroed_username_generator: UserNameGenerator,
    graphql_mock: GraphQLMocker,
    settings_mock: Settings,
    given_name: str,
    surname: str,
    forbidden: list[str],
    expected: str,
) -> None:
    graphql_client = GraphQLClient("http://example.com/graphql")
    alleroed_username_generator.moapi = MOAPI(settings_mock, graphql_client)  # type: ignore

    adsama_it_system = uuid4()

    route1 = graphql_mock.query("read_itsystem_uuid")
    route1.result = {"itsystems": {"objects": [{"uuid": adsama_it_system}]}}

    route2 = graphql_mock.query("read_all_ituser_user_keys_by_itsystem_uuid")
    route2.result = {
        "itusers": {
            "objects": [
                {"validities": [{"user_key": username}]} for username in forbidden
            ]
        }
    }

    # Now clean the list of forbidden usernames and try again
    alleroed_username_generator.forbidden_usernames = forbidden

    employee = Employee(given_name=given_name, surname=surname)
    username = await alleroed_username_generator.generate_username(employee)
    assert username == expected

    assert route1.called
    assert route2.called
