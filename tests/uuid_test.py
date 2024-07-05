from uuid import UUID

from mets_builder.uuid import uuid, underscore_uuid


def test_uuid():
    # This raises error if identifier is not valid UUID
    UUID(uuid())


def test_underscore_uuid():
    identifier = underscore_uuid()
    # First character is underscore
    assert identifier[0] == "_"

    # Rest shoud be valid UUID.
    # This raises error if identifier is not valid UUID
    UUID(identifier[1:])
