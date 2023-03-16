"""Tests for technical object metadata."""
from pathlib import Path

import pytest
import xml_helpers.utils

from mets_builder.metadata import TechnicalObjectMetadata
from mets_builder.serialize import _NAMESPACES


def test_serialization():
    """Test serializing the technical object metadata."""
    data = TechnicalObjectMetadata(
        file_format="video/x-matroska",
        file_format_version="4",
        checksum_algorithm="MD5",
        checksum="3d7dcbd9ca4b5f37189cd2ec85cf0135",
        object_identifier_type="object-identifier-type",
        object_identifier="object-identifier-value"
    )

    result = xml_helpers.utils.serialize(
        data.to_xml_element_tree()
    ).decode("utf-8")

    expected_xml = Path(
        "tests/data/expected_technical_object_metadata.xml"
    ).read_text(encoding="utf-8")

    assert result == expected_xml


def test_identifier_type_not_set():
    """Test that an error is raised if object identifier type is not given
    along with an identifier.
    """
    with pytest.raises(ValueError) as error:
        TechnicalObjectMetadata(
            file_format="video/x-matroska",
            file_format_version="4",
            checksum_algorithm="MD5",
            checksum="checksum-value",
            object_identifier_type=None,
            object_identifier="object-identifier-value"
        )
    assert str(error.value) == (
        "Object identifier type is not given, but object identifier is."
    )


def test_generate_object_identifier():
    """Test that object identifier is generated and type set to 'UUID', if
    identifier is not given by the user.
    """
    object_metadata = TechnicalObjectMetadata(
        file_format="video/x-matroska",
        file_format_version="4",
        checksum_algorithm="MD5",
        checksum="checksum-value",
        agent_identifier_type=None,
        agent_identifier=None
    )
    assert object_metadata.object_identifier_type == "UUID"
    assert object_metadata.object_identifier


def test_user_given_identifier():
    """Test that user can give object identifier and type."""
    object_metadata = TechnicalObjectMetadata(
        file_format="video/x-matroska",
        file_format_version="4",
        checksum_algorithm="MD5",
        checksum="checksum-value",
        object_identifier_type="user-type",
        object_identifier="user-identifier"
    )
    assert object_metadata.object_identifier_type == "user-type"
    assert object_metadata.object_identifier == "user-identifier"


def test_invalid_checksum_algorithm():
    """Test that algorithms not allowed in DPRES specifications cannot be
    set.
    """
    with pytest.raises(ValueError):
        TechnicalObjectMetadata(
            file_format="video/x-matroska",
            file_format_version="4",
            checksum_algorithm="invalid-checksum-algorithm",
            checksum="checksum-value",
            object_identifier_type="user-type",
            object_identifier="user-identifier"
        )


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
    metadata = TechnicalObjectMetadata(
        file_format="video/x-matroska",
        file_format_version="4",
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
    data = TechnicalObjectMetadata(
        file_format="text/plain",
        file_format_version="(:unap)",
        charset=charset,
        checksum_algorithm="MD5",
        checksum="checksum-value"
    )

    result = data.to_xml_element_tree()
    name_element = result.find(
        "premis:objectCharacteristics//premis:formatName",
        namespaces=_NAMESPACES
    )
    assert name_element.text == "text/plain; encoding=" + charset


@pytest.mark.parametrize(
    "invalid_charset",
    (
        ("invalid-charset"),
        ("")
    )
)
def test_invalid_encoding(invalid_charset):
    """Test that invalid encodings raise an error."""
    with pytest.raises(ValueError):
        TechnicalObjectMetadata(
            file_format="text/plain",
            file_format_version="(:unap)",
            file_created_date="2000-01-01T10:11:12",
            charset=invalid_charset,
            checksum_algorithm="MD5",
            checksum="checksum-value"
        )
