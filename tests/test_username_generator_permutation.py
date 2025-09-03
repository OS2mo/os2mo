# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import unittest
from unittest import mock

from hypothesis import given
from hypothesis import strategies as st
from parameterized import parameterized

from ..ad_exceptions import ImproperlyConfigured
from ..user_names import UserNameGen
from ..user_names import UserNameGenMethod2
from ..user_names import UserNameGenPermutation
from ..user_names import UserNameSet
from ..user_names import UserNameSetInAD
from .mocks import MockADParameterReader


class TestUserNameGen(unittest.TestCase):
    _load_setting_path = "integrations.ad_integration.user_names.load_setting"

    @parameterized.expand(
        [
            ("UserNameGenMethod2", UserNameGenMethod2),
            ("UserNameGenUnknown", UserNameGenMethod2),
            ("UserNameGenPermutation", UserNameGenPermutation),
        ]
    )
    def test_override_implementation(self, name, expected_class):
        """Test that `get_implementation` returns the expected implementation
        configured by setting 'integrations.ad_writer.user_names.class'.
        """
        with mock.patch(self._load_setting_path, return_value=lambda: name):
            impl = UserNameGen.get_implementation()
            self.assertIsInstance(impl, expected_class)
            self.assertEqual(len(impl._loaded_occupied_name_sets), 0)

    def test_default_if_no_settings(self):
        """Test that `get_implementation` returns the default implementation
        if 'settings.json' could not be read.
        """

        def raise_filenotfound():
            raise FileNotFoundError()

        with mock.patch(self._load_setting_path, return_value=raise_filenotfound):
            impl = UserNameGen.get_implementation()
            self.assertIsInstance(impl, UserNameGenMethod2)
            self.assertEqual(len(impl._loaded_occupied_name_sets), 0)

    def test_load_occupied_names(self):
        """Test that we can configure `UserNameGen` to load one or more
        `UserNameSet` classes and add their individual sets of occupied names.
        """
        # Get `UserNameGen` implementation which loads occupied usernames from
        # `UserNameSet` (= an empty implementation.)
        impl = self._get_instance("UserNameSet")

        # Assert that we loaded two username sets (from AD and from the
        # `UserNameSet` specified in settings.)
        self.assertEqual(len(impl._loaded_occupied_name_sets), 2)

        # Assert that the first username set is the AD username set.
        self.assertIsInstance(impl._loaded_occupied_name_sets[0], UserNameSetInAD)

        # Assert that the second username set is the one we specified
        # via settings, and is an empty set.
        self.assertIsInstance(impl._loaded_occupied_name_sets[1], UserNameSet)
        self.assertSetEqual(set(impl._loaded_occupied_name_sets[1]), set())

        # Assert that the total set of occupied usernames is equal to
        # the usernames "found" by our mock `ADParameterReader`.
        self.assertSetEqual(
            impl.occupied_names,
            set(impl._loaded_occupied_name_sets[0]),
        )

    def test_load_occupied_names_invalid_name_raises(self):
        with self.assertRaises(ImproperlyConfigured):
            self._get_instance("InvalidUserNameSetName")

    def test_is_username_occupied_is_case_insensitive(self):
        impl = self._get_instance("UserNameSet")
        username = list(impl.occupied_names)[0]
        self.assertEqual(username, username.lower())
        self.assertTrue(impl.is_username_occupied(username.upper()))

    def _get_instance(self, usernameset_class_name: str) -> "UserNameGen":
        cls_names = [usernameset_class_name]
        settings = {
            f"{UserNameGen._setting_prefix}.extra_occupied_name_classes": cls_names
        }
        with self._patch_settings(settings):
            # Use mock `ADParameterReader` in `UserNameSetInAD`
            with mock.patch(
                "integrations.ad_integration.user_names.ADParameterReader",
                new=MockADParameterReader,
            ):
                impl = UserNameGen.get_implementation()
                impl.load_occupied_names()
                return impl

    def _patch_settings(self, settings: dict):
        return mock.patch(
            self._load_setting_path,
            new=lambda name, default=None: lambda: settings.get(name, default),
        )


class TestUserNameGenPermutation(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.instance = UserNameGenPermutation()

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
