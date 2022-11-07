"""Tests for structural map classes."""
import pytest

from mets_builder.digital_object import DigitalObject
from mets_builder.metadata import MetadataBase, MetadataFormat, MetadataType
from mets_builder.structural_map import StructuralMap, StructuralMapDiv


@pytest.mark.parametrize(
    ["invalid_modifications"],
    [
        # pid is not set but pid_type is
        [{"pid": None}],
        # pid_type is not set but pid is
        [{"pid_type": None}],
        # pid contains characters that are not printable US-ASCII
        [{"pid": "ö"}],
        # pid_type contains characters that are not printable US-ASCII
        [{"pid_type": "ö"}]
    ]
)
def test_invalid_init_attributes(invalid_modifications):
    """Test that invalid init attributes for structural map raise an error."""
    init_attributes = {
        "root_div": StructuralMapDiv("test_type"),
        "structural_map_type": "map_type",
        "label": "label",
        "pid": "pid",
        "pid_type": "pid_type"
    }
    init_attributes.update(invalid_modifications)

    with pytest.raises(ValueError):
        StructuralMap(**init_attributes)


def test_iterate_structural_map_div():
    """Test that iterating structural map div iterates through all its nested
    divs.
    """
    # Create structural map with the following div structure:
    # root_div
    # --sub1
    # --sub2
    # ----subsub1
    # ----subsub2
    subsub1 = StructuralMapDiv(div_type="test_type")
    subsub2 = StructuralMapDiv(div_type="test_type")

    sub1 = StructuralMapDiv(div_type="test_type")
    sub2 = StructuralMapDiv(div_type="test_type", divs=[subsub1, subsub2])

    root_div = StructuralMapDiv(div_type="test_type", divs=[sub1, sub2])

    all_divs = {root_div, sub1, sub2, subsub1, subsub2}
    assert set(root_div) == all_divs


def test_iterate_structural_map():
    """Test that iterating structural map iterates through all its nested divs.
    """
    # Create structural map with the following div structure:
    # root_div
    # --sub1
    # --sub2
    # ----subsub1
    # ----subsub2
    subsub1 = StructuralMapDiv(div_type="test_type")
    subsub2 = StructuralMapDiv(div_type="test_type")

    sub1 = StructuralMapDiv(div_type="test_type")
    sub2 = StructuralMapDiv(div_type="test_type", divs=[subsub1, subsub2])

    root_div = StructuralMapDiv(div_type="test_type", divs=[sub1, sub2])
    structural_map = StructuralMap(root_div=root_div)

    all_divs = {root_div, sub1, sub2, subsub1, subsub2}
    assert set(structural_map) == all_divs


def test_add_div_to_div():
    """Test adding a division to a structural map division."""
    div = StructuralMapDiv(div_type="test_type")
    assert div.divs == set()

    nested_div = StructuralMapDiv(div_type="test_type")
    div.add_div(nested_div)
    assert div.divs == {nested_div}


def test_add_metadata_to_div():
    """Test adding metadata to a structural map division."""
    div = StructuralMapDiv(div_type="test_type")
    assert div.metadata == set()

    metadata = MetadataBase(
        metadata_type=MetadataType.DESCRIPTIVE,
        metadata_format=MetadataFormat.OTHER,
        other_format="PAS-special",
        format_version="1.0"
    )
    div.add_metadata(metadata)
    assert div.metadata == {metadata}


def test_add_digital_object_to_div():
    """Test adding a digital object to a structural map division."""
    div = StructuralMapDiv(div_type="test_type")
    assert div.digital_objects == set()

    digital_object = DigitalObject(path_in_sip="path")
    div.add_digital_object(digital_object)
    assert div.digital_objects == {digital_object}
