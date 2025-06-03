"""Tests for digital provenance object metadata."""

import xml_helpers.utils
from mets_builder.metadata import (
    DigitalProvenanceObjectMetadata,
    TechnicalRepresentationObjectMetadata,
)


def test_serialization():
    """Test serializing the digital provenance object metadata object."""
    object_metadata = TechnicalRepresentationObjectMetadata(
        object_identifier_type="UUID",
        object_identifier="00000000-0000-0000-0000-000000000000",
        original_name="test_file.txt",
    )
    object_metadata.add_alternative_identifier(
        identifier_type="local",
        identifier="my-alt-identifier",
    )
    data = DigitalProvenanceObjectMetadata(object_metadata=object_metadata)

    result = xml_helpers.utils.serialize(data.to_xml_element_tree()).decode(
        "utf-8"
    )

    assert "premis:object" in result
