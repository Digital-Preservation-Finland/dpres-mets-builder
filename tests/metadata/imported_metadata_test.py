"""Tests for ImportedMetadata class."""

from pathlib import Path

import pytest

from mets_builder import metadata


def test_importing_metadata_with_invalid_data_path():
    """Test that giving ImportedMetadata an invalid data path results in error.
    """
    with pytest.raises(ValueError) as error:
        metadata.ImportedMetadata(
            data_path=Path("/this/file/does/not/exist"),
            metadata_type=metadata.MetadataType.DESCRIPTIVE,
            metadata_format=metadata.MetadataFormat.DC,
            format_version="1.0"
        )
    assert str(error.value) == (
        "Given path '/this/file/does/not/exist' is not a file."
    )


def test_serializing_imported_metadata_with_data_path():
    """Test that imported metadata is serialized correctly using data path.
    """
    data = metadata.ImportedMetadata(
        data_path=Path("tests/data/imported_metadata.xml"),
        metadata_type=metadata.MetadataType.DESCRIPTIVE,
        metadata_format=metadata.MetadataFormat.OTHER,
        other_format="PAS-special",
        format_version="1.0"
    )
    root_element = data.to_xml_element_tree()

    # The xml file content is
    # <root>
    #   <sub1></sub1>
    #   <sub2></sub2>
    # </root>
    assert root_element.tag == "root"
    assert len(root_element) == 2
    assert root_element[0].tag == "sub1"
    assert root_element[1].tag == "sub2"


def test_serializing_imported_metadata_with_data_string():
    """Test that imported metadata is serialized correctly using a data string.
    """
    data = metadata.ImportedMetadata(
        data_string="<root><sub1></sub1><sub2></sub2></root>",
        metadata_type=metadata.MetadataType.DESCRIPTIVE,
        metadata_format=metadata.MetadataFormat.OTHER,
        other_format="PAS-special",
        format_version="1.0"
    )
    root_element = data.to_xml_element_tree()

    # The xml file content is
    # <root>
    #   <sub1></sub1>
    #   <sub2></sub2>
    # </root>
    assert root_element.tag == "root"
    assert len(root_element) == 2
    assert root_element[0].tag == "sub1"
    assert root_element[1].tag == "sub2"


def test_importing_metadata_without_data_path_or_data_string():
    """Test that giving ImportedMetadata neither data path or data string
    results in error.
    """
    with pytest.raises(ValueError) as error:
        metadata.ImportedMetadata(
            metadata_type=metadata.MetadataType.DESCRIPTIVE,
            metadata_format=metadata.MetadataFormat.DC,
            format_version="1.0"
        )
    assert str(error.value) == (
        "No data path or data string given"
    )


def test_importing_metadata_with_data_path_and_data_string():
    """Test that giving ImportedMetadata both data path and data string results
    in error.
    """
    with pytest.raises(ValueError) as error:
        metadata.ImportedMetadata(
            data_path=Path("/test/path"),
            data_string="<root><sub1></sub1><sub2></sub2></root>",
            metadata_type=metadata.MetadataType.DESCRIPTIVE,
            metadata_format=metadata.MetadataFormat.DC,
            format_version="1.0"
        )
    assert str(error.value) == (
        "Both data path and data string given."
    )
