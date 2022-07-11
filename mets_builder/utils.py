"""Utility functions for mets_builder modules."""
import string


# TODO: In Python 3.8 this can be done with simply
# word.isascii() and word.isprintable()
# and doesn't require a function of its own
def is_printable_us_ascii(word: str) -> bool:
    """Checks whether a string contains only printable US-ASCII
    characters.
    """
    for letter in word:
        if letter not in string.printable:
            return False
    return True
