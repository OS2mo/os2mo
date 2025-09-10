# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from collections.abc import Callable

import pytest
from hypothesis import given
from hypothesis import strategies as st

from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.environments.generate_username import (
    generate_username_permutation,
)
from mo_ldap_import_export.models import Employee


@pytest.fixture
def set_forbidden_usernames(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[[set[str]], None]:
    def inner(usernames: set[str]) -> None:
        monkeypatch.setenv(
            "CONVERSION_MAPPING",
            json.dumps(
                {"username_generator": {"forbidden_usernames": list(usernames)}}
            ),
        )

    return inner


def name2employee(name: list[str]) -> Employee:
    return Employee(given_name=name[0], surname=" ".join(name[1:]))


@given(
    st.lists(
        st.text(
            min_size=1,
            alphabet=st.characters(
                whitelist_characters="bcdfghjklmnpqrstvwxz",
                whitelist_categories=(),
            ),
        ),
        min_size=2,
    )
)
@pytest.mark.usefixtures("minimal_valid_environmental_variables")
async def test_valid_input(name: list[str]) -> None:
    settings = Settings()
    # If `name` has at least two items, each item being a string of at least
    # one consonant, we should be able to create a username.
    await generate_username_permutation(settings, name2employee(name))


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
async def test_suffix_increments(
    set_forbidden_usernames: Callable[[set[str]], None],
) -> None:
    forbidden_usernames: set[str] = set()

    name = ["B", "C", "D"]
    for expected_suffix in range(1, 100):
        set_forbidden_usernames(forbidden_usernames)
        settings = Settings()

        username = await generate_username_permutation(settings, name2employee(name))
        assert username == "bcd%d" % expected_suffix

        forbidden_usernames.add(username)


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
async def test_skips_names_already_taken(
    set_forbidden_usernames: Callable[[set[str]], None],
) -> None:
    forbidden_usernames = {"fnm1", "fnm4"}

    name = ["First Name", "Last-Name"]
    for expected_username in ("fnm2", "fnm3", "fnm5"):
        set_forbidden_usernames(forbidden_usernames)
        settings = Settings()

        username = await generate_username_permutation(settings, name2employee(name))
        assert username == expected_username

        forbidden_usernames.add(username)


@pytest.mark.parametrize(
    "name, expected_username",
    [
        ("Abel Spendabel", "asp1"),  # First name starts with a vowel
        ("Erik Ejegod", "ejg1"),  # Both first name and last name start with a vowel
        ("Erik Episk Ejegod", "eps1"),  # All parts start with a vowel
        ("Gorm Den Gamle", "gdn1"),  # All parts start with a consonant
        ("Ba Ca Da", "bcd1"),  # All parts start with a consonant
        ("Theodor Fælgen", "tfl1"),  # Last name contains non-ASCII character
        ("Øjvind Ørn", "jrn1"),  # All parts begin with non-ASCII characters
        ("Ea Obe", "ebb1"),  # Last name contains just one consonant
        ("Ivan Aaaa", "ivn1"),  # Last name contains *only* vocals
        ("Ab Aaa", "abb1"),  # Only *one* consonant across *all* name parts
    ],
)
@pytest.mark.usefixtures("minimal_valid_environmental_variables")
async def test_by_example(name: str, expected_username: str) -> None:
    settings = Settings()

    name_parts = name.split(maxsplit=1)
    actual_username = await generate_username_permutation(
        settings, name2employee(name_parts)
    )
    assert actual_username == expected_username


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
async def test_check_is_case_insensitive(
    set_forbidden_usernames: Callable[[set[str]], None],
) -> None:
    name = ["Fornavn", "Efternavn"]
    # Generate username (no occupied names yet)
    settings = Settings()
    first_username = await generate_username_permutation(settings, name2employee(name))

    # Add upper-case version of generated username to list of occupied names
    set_forbidden_usernames({first_username.upper()})

    # Generate second username from same name
    settings = Settings()
    second_username = await generate_username_permutation(settings, name2employee(name))

    # Assert new username is different, even when case is ignored
    assert first_username.lower() != second_username.lower()


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
async def test_max_iterations() -> None:
    settings = Settings()

    with pytest.raises(ValueError):
        await generate_username_permutation(settings, name2employee(["A"]))
