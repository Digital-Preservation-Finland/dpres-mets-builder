"""Tests for technical csv metadata."""
from pathlib import Path

import pytest
import xml_helpers

from mets_builder.metadata import TechnicalCSVMetadata


def test_serialization():
    """Test serializing the TechnicalCSVMetadata object."""
    data = TechnicalCSVMetadata(
        filenames=["example-1.csv", "example-2.csv"],
        header=["name", "email"],
        charset="UTF-8",
        delimiter=",",
        record_separator="CR+LF",
        quoting_character="'"
    )

    result = xml_helpers.utils.serialize(
        data.to_xml_element_tree()
    ).decode("utf-8")

    expected_xml = Path(
        "tests/data/expected_technical_csv_metadata.xml"
    ).read_text()

    assert result == expected_xml


def test_giving_filename_as_string():
    """Test that it is possible to give one filename as a string."""
    data = TechnicalCSVMetadata(
        filenames="example.csv",
        header=["name", "email"],
        charset="UTF-8",
        delimiter=",",
        record_separator="CR+LF",
        quoting_character="'"
    )
    result = data.to_xml_element_tree()

    # Find all flatFile-elements
    flat_files = result.xpath(
        "//addml:flatFile",
        namespaces={"addml": "http://www.arkivverket.no/standarder/addml"}
    )
    assert len(flat_files) == 1
    assert flat_files[0].get("name") == "example.csv"


@pytest.mark.parametrize(
    ("files", "result"),
    (
        (
            "example-2.csv",
            ["example-1.csv", "example-2.csv"]
        ),
        (
            ["example-2.csv", "example-3.csv"],
            ["example-1.csv", "example-2.csv", "example-3.csv"]
        )
    )
)
def test_add_files(files, result):
    """Test that files can be added to the metadata after initialization."""
    data = TechnicalCSVMetadata(
        filenames="example-1.csv",
        header=["name", "email"],
        charset="UTF-8",
        delimiter=",",
        record_separator="CR+LF",
        quoting_character="'"
    )
    data.add_files(files)
    assert data.filenames == result
