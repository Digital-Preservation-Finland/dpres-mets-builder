"""Module for different validation utilities."""
import string


# TODO: In Python 3.8 this can be done more simply with
# word.isascii() and word.isprintable()
def is_printable_us_ascii(word: str) -> bool:
    """Checks whether a string contains only printable US-ASCII
    characters.
    """
    for letter in word:
        if letter not in string.printable:
            return False
    return True
