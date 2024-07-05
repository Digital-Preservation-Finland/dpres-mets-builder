"""Module for uuid utilities."""
from uuid import uuid4


def uuid() -> str:
    """Generate a random uuid"""
    return f"{uuid4()}"


def underscore_uuid() -> str:
    """Generate a random uuid with prefixed underscore"""
    return f"_{uuid4()}"
