"""Tests for digital object classes."""
from pathlib import Path
from uuid import UUID

from mets_builder import metadata
from mets_builder.digital_object import (DigitalObject, DigitalObjectBase,
                                         DigitalObjectStream)


def test_add_metadata():
    """Test adding metadata to a digital object or a stream."""
    digital_object = DigitalObjectBase()
    assert digital_object.metadata == set()

    data = metadata.ImportedMetadata(
        data_path=Path("tests/data/imported_metadata.xml"),
        metadata_type=metadata.MetadataType.DESCRIPTIVE,
        metadata_format=metadata.MetadataFormat.OTHER,
        other_format="PAS-special",
        format_version="1.0"
    )
    digital_object.add_metadata(data)
    assert digital_object.metadata == {data}


def test_generated_identifier():
    """Test that if identifier is not given, an UUID identifier is generated
    for digital object.
    """
    digital_object = DigitalObject(path_in_sip="path", identifier=None)

    # First character is underscore
    assert digital_object.identifier[0] == "_"

    # Rest shoud be valid UUID.
    # This raises error if identifier is not valid UUID
    UUID(digital_object.identifier[1:])


def test_add_stream_to_digital_object():
    """Test adding stream to a digital object."""
    digital_object = DigitalObject(path_in_sip="path")
    assert digital_object.streams == set()

    stream = DigitalObjectStream()
    digital_object.add_stream(stream)
    assert digital_object.streams == {stream}
