"""Tests for metadata objects."""
from datetime import datetime, timezone
from uuid import UUID

import pytest

from mets_builder import metadata


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
        metadata.MetadataBase(
            metadata_type="technical",
            metadata_format=metadata_format,
            other_format=other_format,
            format_version="1.0"
        )


def test_metadatabase_with_other_format():
    """Test that other_format overrides metadata format."""
    data = metadata.MetadataBase(
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
        metadata.MetadataBase(
            metadata_type="invalid",
            metadata_format=metadata.MetadataFormat.PREMIS_OBJECT,
            format_version="1.0"
        )


def test_generated_identifier():
    """Test that if identifier is not given, an uuid identifier is generated.
    """
    data = metadata.MetadataBase(
        metadata_type="technical",
        metadata_format="PREMIS:OBJECT",
        format_version="1.0",
        identifier=None
    )

    # First character is underscore
    assert data.identifier[0] == "_"

    # Rest shoud be valid UUID.
    # This raises error if identifier is not valid UUID
    UUID(data.identifier[1:])


def test_generated_created_time():
    """Test that if create time is not given, current time is used."""
    data = metadata.MetadataBase(
        metadata_type="technical",
        metadata_format="PREMIS:OBJECT",
        format_version="1.0",
        created=None
    )

    # UTC time is used
    assert data.created.tzinfo == timezone.utc
    # Date matches to current date
    assert data.created.date() == datetime.now().date()
