"""Tests for technical CSV metadata."""
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
    """Test that it is not possible to give filename as a string."""

    with pytest.raises(TypeError) as error:
        TechnicalCSVMetadata(
            filenames="example.csv",
            header=["name", "email"],
            charset="UTF-8",
            delimiter=",",
            record_separator="CR+LF",
            quoting_character="'"
        )
    assert str(error.value) == (
        "Given 'filenames' is a single string. Give an iterable of strings as "
        "the 'filenames' attribute value."
    )


def test_add_files():
    """Test that files can be added to the metadata after initialization."""
    data = TechnicalCSVMetadata(
        filenames=["example-1.csv"],
        header=["name", "email"],
        charset="UTF-8",
        delimiter=",",
        record_separator="CR+LF",
        quoting_character="'"
    )
    data.add_files(["example-2.csv", "example-3.csv"])
    assert data.filenames == [
        "example-1.csv", "example-2.csv", "example-3.csv"
    ]


def test_adding_files_as_string():
    """Test that files can not be added as strings."""
    data = TechnicalCSVMetadata(
        filenames=["example-1.csv"],
        header=["name", "email"],
        charset="UTF-8",
        delimiter=",",
        record_separator="CR+LF",
        quoting_character="'"
    )

    with pytest.raises(TypeError) as error:
        data.add_files("example-2.csv")
    assert str(error.value) == (
        "Given 'filenames' is a single string. Give an iterable of strings as "
        "the 'filenames' argument."
    )
