"""Tests for metadata objects."""
import pytest

from mets_builder import metadata
from mets_builder.metadata import Metadata


class DummyMetadata(Metadata):
    """Class for for testing Metadata."""
    def _to_xml_element_tree(self, state):
        pass


@pytest.mark.parametrize(
    ["metadata_format", "other_format"],
    [
        # Invalid format
        ("invalid", None),
        # Format is OTHER but other_format is not set
        ("OTHER", None),
        # No format or or other_format
        (None, None)
    ]
)
def test_metadatabase_invalid_format(metadata_format, other_format):
    """Test creating metadataobject with invalid format configuration."""
    with pytest.raises(ValueError):
        DummyMetadata(
            metadata_type="technical",
            metadata_format=metadata_format,
            other_format=other_format,
            format_version="1.0"
        )


def test_metadatabase_with_other_format():
    """Test that other_format overrides metadata format."""
    data = DummyMetadata(
        metadata_type="technical",
        metadata_format="PREMIS:OBJECT",
        other_format="special_format",
        format_version="1.0"
    )
    assert data.metadata_format == metadata.MetadataFormat.OTHER
    assert data.other_format == "special_format"


def test_metadatabase_invalid_type():
    """Test creating metadataobject with invalid type."""
    with pytest.raises(ValueError):
        DummyMetadata(
            metadata_type="invalid",
            metadata_format=metadata.MetadataFormat.PREMIS_OBJECT,
            format_version="1.0"
        )


@pytest.mark.parametrize(
    ["metadata_type", "expected_result"],
    [
        ("technical", True),
        ("digital provenance", True),
        ("descriptive", False)
    ]
)
def test_is_administrative(metadata_type, expected_result):
    """Test if metadata object can tell correctly that it is administrative
    metadata.
    """
    data = DummyMetadata(
        metadata_type=metadata_type,
        metadata_format=None,
        other_format="PAS-special",
        format_version="1.0"
    )
    assert data.is_administrative == expected_result


@pytest.mark.parametrize(
    ["metadata_type", "expected_result"],
    [
        ("technical", False),
        ("digital provenance", False),
        ("descriptive", True)
    ]
)
def test_is_descriptive(metadata_type, expected_result):
    """Test if metadata object can tell correctly that it is descriptive
    metadata.
    """
    data = DummyMetadata(
        metadata_type=metadata_type,
        metadata_format=None,
        other_format="PAS-special",
        format_version="1.0"
    )
    assert data.is_descriptive == expected_result
