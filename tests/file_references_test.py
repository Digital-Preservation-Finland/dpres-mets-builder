"""Tests for file reference classes."""
import pytest

from mets_builder.digital_object import DigitalObject
from mets_builder.file_references import FileGroup, FileReferences


def test_add_file_group_to_file_references():
    """Test adding a file group to FileReferences instance."""
    file_references = FileReferences()
    assert file_references.file_groups == set()

    group = FileGroup()
    file_references.add_file_group(group)
    assert file_references.file_groups == {group}


def test_add_digital_object_to_file_group():
    """Test adding a digital object to a file group."""
    group = FileGroup()
    assert group.digital_objects == set()

    digital_object = DigitalObject("file_path")
    group.add_digital_object(digital_object)
    assert group.digital_objects == {digital_object}


def test_generate_file_references():
    """Test generating file references automatically."""
    digital_objects = {
        DigitalObject(path="path/1"),
        DigitalObject(path="path/2"),
        DigitalObject(path="path/3")
    }

    file_references = FileReferences.generate_file_references(digital_objects)

    # The generated file references have one file group with all the files in
    # it
    assert len(file_references.file_groups) == 1
    group = file_references.file_groups.pop()
    assert group.digital_objects == set(digital_objects)


def test_generate_file_references_with_no_files():
    """Test that generating file references without digital objects raises an
    error.
    """
    with pytest.raises(ValueError) as error:
        FileReferences.generate_file_references(digital_objects=[])
    assert str(error.value) == (
        "No digital objects given, cannot generate file references."
    )
