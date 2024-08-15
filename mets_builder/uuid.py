"""Module for generating UUIDs"""
from uuid import uuid4


def uuid() -> str:
    """Generate a random uuid

    This function is a thin wrapper for the 'uuid4' function the standard
    library 'uuid' module. This function exist so we don't have to use both the
    standard library 'uuid' module and this module both regular UUIDs and UUIDs
    prefixed with an underscore are needed

    :returns: UUID
    """
    return f"{uuid4()}"


def underscore_uuid() -> str:
    """Generate a random uuid with prefixed underscore

    Some identifier fields in METS schema start with an underscore. This
    function is a thin wrapper for the 'uuid4' function the standard library
    'uuid' module which  prefixed with an underscore to the UUID.

    :returns: UUID prefix with an underscore
    """
    return f"_{uuid4()}"
