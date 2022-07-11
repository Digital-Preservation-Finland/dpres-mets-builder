"""Tests for utils.py."""
import pytest

import mets_builder.utils


@pytest.mark.parametrize(
    ["value", "result"],
    [
        ("foo", True),
        (".!?", True),
        ("a\nb", True),
        ("ä", False),
    ]
)
def test_is_printable_us_ascii(value, result):
    """Test function checktin whether a string contains only printable US-ASCII
    characters.
    """
    assert mets_builder.utils.is_printable_us_ascii(value) == result
