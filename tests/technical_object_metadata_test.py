"""Tests for technical object metadata."""
from pathlib import Path

import pytest
import xml_helpers.utils

from mets_builder.metadata import TechnicalObjectMetadata


def test_serialization():
    """Test serializing the technical object metadata."""
    data = TechnicalObjectMetadata(
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
        agent_identifier_type=None,
        agent_identifier=None
    )
    assert object_metadata.object_identifier_type == "UUID"
    assert object_metadata.object_identifier


def test_user_given_identifier():
    """Test that user can give object identifier and type."""
    object_metadata = TechnicalObjectMetadata(
        object_identifier_type="user-type",
        object_identifier="user-identifier"
    )
    assert object_metadata.object_identifier_type == "user-type"
    assert object_metadata.object_identifier == "user-identifier"
