# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import unittest

from hypothesis import given
from hypothesis import strategies as st
from parameterized import parameterized

from ..user_names import UserNameGenPermutation


class TestUserNameGenPermutation(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.instance = UserNameGenPermutation()

    def test_is_username_occupied_is_case_insensitive(self):
        username = list(self.instance.occupied_names)[0]
        self.assertEqual(username, username.lower())
        self.assertTrue(self.instance.is_username_occupied(username.upper()))

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
        # If `name` has at least two items, each item being a string of at least
        # one consonant, we should be able to create a username.
        self.instance.create_username(name)

    def test_suffix_increments(self):
        name = ["B", "C", "D"]
        for expected_suffix in range(1, 100):
            username = self.instance.create_username(name)
            self.assertEqual(username, "bcd%d" % expected_suffix)

    def test_skips_names_already_taken(self):
        name = ["First Name", "Last-Name"]
        self.instance.add_occupied_names({"fnm1", "fnm4"})
        for expected_username in ("fnm2", "fnm3", "fnm5"):
            username = self.instance.create_username(name)
            self.assertEqual(username, expected_username)

    @parameterized.expand(
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
        ]
    )
    def test_by_example(self, name, expected_username):
        name = name.split(maxsplit=1)
        actual_username = self.instance.create_username(name)
        self.assertEqual(actual_username, expected_username)

    def test_check_is_case_insensitive(self):
        name = ["Fornavn", "Efternavn"]
        # Generate username (no occupied names yet)
        first_username = self.instance.create_username(name)
        # Add upper-case version of generated username to list of occupied names
        self.instance.add_occupied_names({first_username.upper()})
        # Generate second username from same name
        second_username = self.instance.create_username(name)
        # Assert new username is different, even when case is ignored
        self.assertNotEqual(first_username.lower(), second_username.lower())

    def test_max_iterations(self):
        with self.assertRaises(ValueError):
            self.instance.create_username(["A"])
