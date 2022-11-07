"""Tests for validation module."""
import pytest

from mets_builder import validation


@pytest.mark.parametrize(
    ["word", "expected_result"],
    [
        ("Aa", True),
        ("0123456789", True),
        ("I only have printable US-ASCII characters", True),
        ('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~', True),
        ("å", False),
        ("ä", False),
        ("ö", False),
        ("🐸", False)
    ]
)
def test_is_printable_us_ascii(word, expected_result):
    """Test that a validation function can tell whether a word only has
    printable US-ASCII characters.
    """
    assert validation.is_printable_us_ascii(word) == expected_result
