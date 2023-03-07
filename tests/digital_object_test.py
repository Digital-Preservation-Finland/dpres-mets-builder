"""Tests for digital object classes."""
from pathlib import Path
from uuid import UUID

import pytest

from mets_builder import metadata
from mets_builder.digital_object import (DigitalObject, DigitalObjectBase,
                                         DigitalObjectStream)


def test_add_metadata():
    """Test adding metadata to a digital object or a stream."""
    digital_object = DigitalObjectBase()
    assert digital_object.metadata == set()

    data = metadata.ImportedMetadata(
        data_path=Path("tests/data/imported_metadata.xml"),
        metadata_type=metadata.MetadataType.TECHNICAL,
        metadata_format=metadata.MetadataFormat.OTHER,
        other_format="PAS-special",
        format_version="1.0"
    )
    digital_object.add_metadata(data)
    assert digital_object.metadata == {data}


def test_add_descriptive_metadata():
    """Test that adding descriptive metadata raises an error, and gives helpful
    information where descriptive metadata should be added to.
    """
    digital_object = DigitalObjectBase()
    assert digital_object.metadata == set()

    data = metadata.ImportedMetadata(
        data_path=Path("tests/data/imported_metadata.xml"),
        metadata_type=metadata.MetadataType.DESCRIPTIVE,
        metadata_format=metadata.MetadataFormat.OTHER,
        other_format="PAS-special",
        format_version="1.0"
    )

    with pytest.raises(ValueError) as error:
        digital_object.add_metadata(data)
    assert str(error.value) == (
        "Added metadata is descriptive metadata. Descriptive metadata should "
        "be added to a div in a structural map."
    )


def test_generated_identifier():
    """Test that if identifier is not given, an UUID identifier is generated
    for digital object.
    """
    digital_object = DigitalObject(sip_filepath="path", identifier=None)

    # First character is underscore
    assert digital_object.identifier[0] == "_"

    # Rest shoud be valid UUID.
    # This raises error if identifier is not valid UUID
    UUID(digital_object.identifier[1:])


def test_add_stream_to_digital_object():
    """Test adding stream to a digital object."""
    digital_object = DigitalObject(sip_filepath="path")
    assert digital_object.streams == set()

    stream = DigitalObjectStream()
    digital_object.add_stream(stream)
    assert digital_object.streams == {stream}


def test_sip_filepath_is_relative():
    """Test that giving absolute file path as digital object's sip filepath
    raises an error.
    """
    with pytest.raises(ValueError) as error:
        DigitalObject(sip_filepath="/path")
    assert str(error.value) == (
        "Given SIP file path '/path' is not a relative path."
    )


@pytest.mark.parametrize(
    "sip_filepath",
    [
        (".."),
        ("a/b/c/d/../../../../../b"),
        ("../../etc/passwd")
    ]
)
def test_sip_filepath_does_not_point_outside_sip(sip_filepath):
    """Test that given SIP filepath does not point outside the SIP."""
    with pytest.raises(ValueError) as error:
        DigitalObject(sip_filepath=sip_filepath)
    assert str(error.value) == (
        f"Given SIP file path '{sip_filepath}' points outside the SIP root "
        "directory."
    )
