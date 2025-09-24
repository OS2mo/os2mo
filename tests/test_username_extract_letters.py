# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import string

import pytest
from hypothesis import given
from hypothesis import strategies as st
from more_itertools import first

from mo_ldap_import_export.environments.generate_username import _extract_letters


def test_extract_letters_empty_list_error() -> None:
    """Test _extract_letters with an empty list which should raise IndexError."""
    with pytest.raises(ValueError):
        _extract_letters([])


@pytest.mark.parametrize(
    "name",
    [
        # Empty strings
        [""],
        ["", ""],
        ["", "", ""],
        # Valid ASCII characters that are not letters
        ["-"],
        [":"],
        ["="],
        ["?"],
        ["1"],
        ["7"],
        # +BB is split on "+" to ['', 'BB'] which fails.
        # TODO: This is likely a mistake due to a poorly written regex
        #       Specifically: r"[\-\s+]" not realizing that it matches "-", "\s" and "+"
        #       but instead expecting it to match "-" and "\s+"
        ["+BB"],
    ],
)
def test_extract_letters_assertion_error(name: list[str]) -> None:
    """Test _extract_letters with invalid inputs expecting AssertionErrors."""
    with pytest.raises(AssertionError) as exc_info:
        _extract_letters(name)
    assert "first name part must contain at least one ASCII letter" in str(
        exc_info.value
    )


@pytest.mark.parametrize(
    "name",
    [
        # Not enough unique consonants to fill username
        ["A"],
        ["AB"],
        ["B"],
        ["Audio"],
        ["Adieu"],
        # No consonants after first letter
        ["Aeo", "Iea"],
    ],
)
def test_extract_letters_value_error(name: list[str]) -> None:
    """Test _extract_letters with names that should raise a ValueError."""
    with pytest.raises(ValueError) as exc_info:
        _extract_letters(name)
    assert "cannot create username" in str(exc_info.value)


@pytest.mark.parametrize(
    "name, expected_letters",
    [
        # Minimal examples, single name
        (["BB"], ["b", "b", "b"]),
        (["BC"], ["b", "b", "c"]),
        (["ABC"], ["a", "b", "c"]),
        (["ABCD"], ["a", "b", "c"]),
        (["BCD"], ["b", "b", "c"]),
        (["BCDE"], ["b", "b", "c"]),
        # Minimal examples, multiple single character names
        (["B", "B"], ["b", "b", "b"]),
        (["B", "C"], ["b", "c", "c"]),
        (["A", "B", "C"], ["a", "b", "c"]),
        (["A", "B", "C", "D"], ["a", "b", "c"]),
        (["B", "C", "D"], ["b", "c", "d"]),
        (["B", "C", "D", "E"], ["b", "c", "d"]),
        # Minimal examples, two multi character names
        (["A", "BCD"], ["a", "b", "c"]),
        (["AB", "CD"], ["a", "c", "d"]),
        (["ABC", "D"], ["a", "d", "c"]),
        # Simple case with two names
        (["First", "Last"], ["f", "l", "s"]),
        # Three names
        (["First", "Middle", "Last"], ["f", "m", "d"]),
        # Second name has no consonants, should skip to third
        (["First", "Ae", "Last"], ["f", "l", "s"]),
        # Second name is short on consonants, should loop back to first name for third letter
        (["Anders", "Bo"], ["a", "b", "d"]),
        # Second name has enough consonants
        (["First", "Only"], ["f", "n", "l"]),
        # Second name has no consonants, should loop to first name for second and third
        (["First", "Oa"], ["f", "f", "r"]),
        # Name with hyphens and spaces
        (["First-Name", "Last Name"], ["f", "n", "m"]),
        # Non-ASCII characters
        (["Æble", "Grød"], ["b", "g", "r"]),
        # Single name part
        (["Firstname"], ["f", "f", "r"]),
        # Vowel as first letter
        (["Apple", "Banana"], ["a", "b", "n"]),
        # All caps
        (["FIRST", "LAST"], ["f", "l", "s"]),
        # Mixed case
        (["FiRsT", "LaSt"], ["f", "l", "s"]),
        # Single-letter names
        (["A", "B"], ["a", "b", "b"]),
        # Empty name part
        (["First", "", "Last"], ["f", "l", "s"]),
        # Consonant-lacking second name
        (["F", "aeiou"], ["f", "f", "f"]),
        # Consonants only in third name part
        (["aeo", "iea", "Test"], ["a", "t", "s"]),
        # Non-alphabetic characters in later name parts should be ignored
        (["test", "-"], ["t", "t", "s"]),
        # Complex splitting of name parts
        (["A B-C", "D"], ["a", "b", "c"]),
        # Name parts consisting only of vowels (after first letter)
        (["Consonant", "Aeiou", "Ieaou"], ["c", "c", "n"]),
    ],
)
def test_extract_letters_happy_path(name: list[str], expected_letters: str) -> None:
    """Test _extract_letters with various valid inputs."""
    assert _extract_letters(name) == expected_letters


def count_consonants(s: str) -> int:
    consonants = "".join(set(string.ascii_lowercase) - set("aeiouy"))
    return sum(char in consonants for char in s.lower())


@given(
    st.lists(
        st.text(
            alphabet=st.characters(
                # Any unicode character is okay, as long as it is not:
                # - og + due to our regex splitting, a whitespace nor control character
                # For more details on the "+" matching check the "+BB" test-case comment
                codec="utf-8",
                blacklist_characters=["-", "+"],
                blacklist_categories=("Z", "C"),
            )
        ),
        # Name must have atleast one part
        min_size=1,
    )
    .filter(
        # The first name part must contain an ascii letter
        lambda xs: any(char in string.ascii_lowercase for char in first(xs).lower())
    )
    .filter(
        # There must be atleast 2 consonants in the name
        lambda xs: count_consonants("".join(xs)) >= 2
    )
)
def test_extract_letters_always_return_3_letters(name: list[str]) -> None:
    result = _extract_letters(name)
    assert isinstance(result, list)
    assert len(result) == 3
    for letter in result:
        assert isinstance(letter, str)
        assert len(letter) == 1
        assert letter in string.ascii_lowercase
