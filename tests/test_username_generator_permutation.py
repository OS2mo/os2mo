# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import unittest

from hypothesis import given
from hypothesis import strategies as st
from more_itertools import one

from mo_ldap_import_export.environments.generate_username import UserNameGenPermutation


class TestUserNameGenPermutation(unittest.TestCase):
    def test_is_username_occupied_is_case_insensitive(self):
        username_generator = UserNameGenPermutation()

        assert username_generator.occupied_names == set()
        username_generator.add_occupied_names({"hans"})

        username = one(username_generator.occupied_names)
        assert username == username.lower()
        assert username_generator.is_username_occupied(username.upper())

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
    def test_valid_input(self, name):
        username_generator = UserNameGenPermutation()

        # If `name` has at least two items, each item being a string of at least
        # one consonant, we should be able to create a username.
        username_generator.create_username(name)

    def test_suffix_increments(self):
        username_generator = UserNameGenPermutation()

        name = ["B", "C", "D"]
        for expected_suffix in range(1, 100):
            username = username_generator.create_username(name)
            assert username == "bcd%d" % expected_suffix

    def test_skips_names_already_taken(self):
        username_generator = UserNameGenPermutation()

        name = ["First Name", "Last-Name"]
        username_generator.add_occupied_names({"fnm1", "fnm4"})
        for expected_username in ("fnm2", "fnm3", "fnm5"):
            username = username_generator.create_username(name)
            assert username == expected_username

    def test_by_example(self):
        username_generator = UserNameGenPermutation()

        cases = [
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
        ]
        for name, expected_username in cases:
            with self.subTest((name, expected_username)):
                name = name.split(maxsplit=1)
                actual_username = username_generator.create_username(name)
                assert actual_username == expected_username

    def test_check_is_case_insensitive(self):
        username_generator = UserNameGenPermutation()

        name = ["Fornavn", "Efternavn"]
        # Generate username (no occupied names yet)
        first_username = username_generator.create_username(name)
        # Add upper-case version of generated username to list of occupied names
        username_generator.add_occupied_names({first_username.upper()})
        # Generate second username from same name
        second_username = username_generator.create_username(name)
        # Assert new username is different, even when case is ignored
        assert first_username.lower() != second_username.lower()

    def test_max_iterations(self):
        username_generator = UserNameGenPermutation()

        with self.assertRaises(ValueError):
            username_generator.create_username(["A"])
