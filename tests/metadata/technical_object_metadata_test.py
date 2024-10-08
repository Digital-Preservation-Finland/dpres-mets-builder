"""Tests for technical object metadata."""
from pathlib import Path

import pytest
import xml_helpers.utils

from mets_builder.metadata import (TechnicalBitstreamObjectMetadata,
                                   TechnicalFileObjectMetadata,
                                   TechnicalObjectMetadata)
from mets_builder.serialize import NAMESPACES


def test_abstract_init_not_allowed():
    """
    Test that creating an instance of the abstract TechnicalObjectMetadata
    class is not allowed.
    """
    with pytest.raises(TypeError) as error:
        TechnicalObjectMetadata()
    assert str(error.value).startswith(
        "Can't instantiate abstract class TechnicalObjectMetadata"
    )


def test_file_serialization():
    """Test serializing the technical file object metadata."""
    container = TechnicalFileObjectMetadata(
        file_format="video/x-matroska",
        file_format_version="4",
        file_created_date="2000-01-01T10:11:12",
        checksum_algorithm="MD5",
        checksum="3d7dcbd9ca4b5f37189cd2ec85cf0135",
        object_identifier_type="object-identifier-type",
        object_identifier="object-identifier-value",
        original_name="original-name",
        format_registry_name="format-registry-name",
        format_registry_key="format-registry-key",
        creating_application="application-name",
        creating_application_version="1.0"
    )

    # Related metadata
    object_metadatas = []
    for i in range(6):
        object_metadatas.append(
            TechnicalFileObjectMetadata(
                file_format="file-format",
                file_format_version="file-format-version",
                file_created_date="2000-01-01T00:00:00",
                checksum_algorithm="MD5",
                checksum="checksum-value",
                object_identifier_type="test-type",
                object_identifier=f"related-{i}"
            )
        )

    # Relationship group 1 - type-1, subtype-1
    container.add_relationship(
        technical_object_metadata=object_metadatas[0],
        relationship_type="type-1",
        relationship_subtype="subtype-1"
    )
    container.add_relationship(
        technical_object_metadata=object_metadatas[1],
        relationship_type="type-1",
        relationship_subtype="subtype-1"
    )
    container.add_relationship(
        technical_object_metadata=object_metadatas[2],
        relationship_type="type-1",
        relationship_subtype="subtype-1"
    )

    # Relationship group 2 - type-1, subtype-2
    container.add_relationship(
        technical_object_metadata=object_metadatas[3],
        relationship_type="type-1",
        relationship_subtype="subtype-2"
    )
    container.add_relationship(
        technical_object_metadata=object_metadatas[4],
        relationship_type="type-1",
        relationship_subtype="subtype-2"
    )

    # Relationship group 3 - type-2, subtype-2
    container.add_relationship(
        technical_object_metadata=object_metadatas[5],
        relationship_type="type-2",
        relationship_subtype="subtype-2"
    )

    result = xml_helpers.utils.serialize(
        container.to_xml_element_tree()
    ).decode("utf-8")

    expected_xml = Path(
        "tests/data/expected_technical_file_object_metadata.xml"
    ).read_text(encoding="utf-8")

    assert result == expected_xml


def test_bitstream_serialization():
    """Test serializing the technical bitstream metadata"""
    bitstream = TechnicalBitstreamObjectMetadata(
        file_format="video/x-ffv",
        file_format_version="4",
        object_identifier_type="UUID",
        object_identifier="615a96f5-dce7-4471-b5a5-77d9150322ce",
    )

    result = xml_helpers.utils.serialize(
        bitstream.to_xml_element_tree()
    ).decode("utf-8")

    expected_xml = Path(
        "tests/data/expected_technical_bitstream_object_metadata.xml"
    ).read_text(encoding="utf-8")

    assert result == expected_xml


def test_generate_object_identifier():
    """Test that object identifier is generated and type set to 'UUID', if
    identifier is not given by the user.
    """
    object_metadata = TechnicalFileObjectMetadata(
        file_format="video/x-matroska",
        file_format_version="4",
        file_created_date="2000-01-01T10:11:12",
        checksum_algorithm="MD5",
        checksum="checksum-value"
    )
    assert object_metadata.object_identifier_type == "UUID"
    assert object_metadata.object_identifier


def test_user_given_identifier():
    """Test that user can give object identifier and type."""
    object_metadata = TechnicalFileObjectMetadata(
        file_format="video/x-matroska",
        file_format_version="4",
        file_created_date="2000-01-01T10:11:12",
        checksum_algorithm="MD5",
        checksum="checksum-value",
        object_identifier_type="user-type",
        object_identifier="user-identifier"
    )
    assert object_metadata.object_identifier_type == "user-type"
    assert object_metadata.object_identifier == "user-identifier"


@pytest.mark.parametrize(
    "checksum_algorithm",
    (
        ("MD5"),
        ("SHA-1"),
        ("SHA-224"),
        ("SHA-256"),
        ("SHA-384"),
        ("SHA-512")
    )
)
def test_valid_checksum_algorithm(checksum_algorithm):
    """Test that algorithms allowed in DPRES specifications can be set."""
    metadata = TechnicalFileObjectMetadata(
        file_format="video/x-matroska",
        file_format_version="4",
        file_created_date="2000-01-01T10:11:12",
        checksum_algorithm=checksum_algorithm,
        checksum="checksum-value",
        object_identifier_type="user-type",
        object_identifier="user-identifier"
    )
    assert metadata.checksum_algorithm


@pytest.mark.parametrize(
    "charset",
    (
        ("ISO-8859-15"),
        ("UTF-8"),
        ("UTF-16"),
        ("UTF-32")
    )
)
def test_valid_encodings(charset):
    """Test that if encoding is given, it is appended to mimetype when
    metadata is serialized.
    """
    data = TechnicalFileObjectMetadata(
        file_format="text/plain",
        file_format_version="(:unap)",
        file_created_date="2000-01-01T10:11:12",
        charset=charset,
        checksum_algorithm="MD5",
        checksum="checksum-value"
    )

    result = data.to_xml_element_tree()
    name_element = result.find(
        "premis:objectCharacteristics//premis:formatName",
        namespaces=NAMESPACES
    )
    assert name_element.text == "text/plain; charset=" + charset


@pytest.mark.parametrize(
    ("invalid_init_params", "error_message"),
    (
        (
            {"file_format": ""},
            "Empty value not allowed for 'file_format'"
        ),
        (
            {"file_format_version": ""},
            "Empty value not allowed for 'file_format_version'"
        ),
        (
            {"checksum": ""},
            "Empty value not allowed for 'checksum'"
        ),
        (
            {"object_identifier_type": ""},
            "Object identifier is given but object identifier type is not."
        ),
        (
            {"object_identifier": ""},
            "Object identifier type is given but object identifier is not."
        ),
        (
            {"format_registry_name": ""},
            "Format registry key is given but format registry name is not."
        ),
        (
            {"format_registry_key": ""},
            "Format registry name is given but format registry key is not."
        ),
        (
            {"creating_application": ""},
            ("Creating application version is given but creating application "
             "is not.")
        ),
        (
            {"creating_application_version": ""},
            ("Creating application is given but creating application version "
             "is not.")
        ),
        (
            {"checksum_algorithm": ""},
            "Empty value not allowed for 'checksum_algorithm'"
        ),
        (
            {"checksum_algorithm": "invalid"},
            "'invalid' is not a valid ChecksumAlgorithm"
        ),
        (
            {"charset": ""},
            "'' is not a valid Charset"
        ),
        (
            {"charset": "invalid"},
            "'invalid' is not a valid Charset"
        ),
    )
)
def test_invalid_file_parameters(invalid_init_params, error_message):
    """
    Test that invalid parameter values for TechnicalFileObjectMetadata raise
    a ValueError.
    """
    init_params = {
        "file_format": "video/x-matroska",
        "file_format_version": "4",
        "file_created_date": "2000-01-01T10:11:12",
        "checksum_algorithm": "MD5",
        "checksum": "3d7dcbd9ca4b5f37189cd2ec85cf0135",
        "object_identifier_type": "object-identifier-type",
        "object_identifier": "object-identifier-value",
        "original_name": "original-name",
        "format_registry_name": "format-registry-name",
        "format_registry_key": "format-registry-key",
        "creating_application": "application-name",
        "creating_application_version": "1.0"
    }
    init_params.update(invalid_init_params)

    with pytest.raises(ValueError) as error:
        TechnicalFileObjectMetadata(**init_params)
    assert str(error.value) == error_message


def test_unapplicable_file_format_version():
    """Test that when file format version is given as unapplicable, the value
    is not shown in the final serialization.
    """
    object_metadata = TechnicalFileObjectMetadata(
        file_format="Text/csv",
        file_format_version="(:unap)",
        file_created_date="2000-01-01T00:00:00",
        checksum_algorithm="MD5",
        checksum="checksum-value"
    )
    serialized = object_metadata.to_xml_element_tree()

    # Find the format version element, if it exists
    format_version_element = serialized.xpath(
        "//premis:formatVersion", namespaces=NAMESPACES
    )
    assert len(format_version_element) == 0
