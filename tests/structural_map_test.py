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

    nested_divs = {sub1, sub2, subsub1, subsub2}
    assert set(root_div) == nested_divs


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


def test_get_root_div():
    """Test getting the root div of a div."""
    subsubdiv = StructuralMapDiv("test_type")
    subdiv = StructuralMapDiv("test_type", divs=[subsubdiv])
    root_div = StructuralMapDiv("test_type", divs=[subdiv])

    assert root_div.root_div == root_div
    assert subdiv.root_div == root_div
    assert subsubdiv.root_div == root_div


def test_add_duplicate_div_to_div_tree():
    """Test that adding a div that already exists in the div tree raises an
    error.
    """
    subsubdiv = StructuralMapDiv("test_type")
    subdiv = StructuralMapDiv("test_type", divs=[subsubdiv])
    root_div = StructuralMapDiv("test_type", divs=[subdiv])

    # Add a div to itself
    with pytest.raises(ValueError):
        root_div.add_div(root_div)

    # Add a div that already exists lower in tree
    with pytest.raises(ValueError):
        root_div.add_div(subsubdiv)

    # Add a div that already exists higher up in the tree
    with pytest.raises(ValueError):
        subsubdiv.add_div(root_div)

    # Add a div that lower in its tree contains a div that already exists in
    # the parent div tree
    new_div = StructuralMapDiv("test_type", divs=[root_div])
    with pytest.raises(ValueError):
        subdiv.add_div(new_div)

    # Add a div to its sibling
    subsubdiv_sibling = StructuralMapDiv("test_type")
    subdiv.add_div(subsubdiv_sibling)
    with pytest.raises(ValueError):
        subsubdiv.add_div(subsubdiv_sibling)


def test_add_duplicate_object_to_div():
    """Test that adding a digital object twice to a div raises an error."""
    subsubdiv = StructuralMapDiv("test_type")
    subdiv = StructuralMapDiv("test_type", divs=[subsubdiv])
    root_div = StructuralMapDiv("test_type", divs=[subdiv])

    digital_object = DigitalObject("path")
    subdiv.add_digital_object(digital_object)

    # Adding the object second time to the same div
    with pytest.raises(ValueError):
        subdiv.add_digital_object(digital_object)

    # Adding the object to parent div
    with pytest.raises(ValueError):
        root_div.add_digital_object(digital_object)

    # Adding the object to child div
    with pytest.raises(ValueError):
        subsubdiv.add_digital_object(digital_object)

    # Adding the object to a sibling
    subdiv_sibling = StructuralMapDiv("test_type")
    root_div.add_div(subdiv_sibling)
    with pytest.raises(ValueError):
        subdiv_sibling.add_digital_object(digital_object)


def test_add_div_with_duplicate_digital_object_to_div():
    """Test that adding a div to a div that contains a digital object that
    already exists in the div tree fails.
    """
    digital_object = DigitalObject("path")

    subdiv_1 = StructuralMapDiv("test_type", digital_objects=[digital_object])
    root_div_1 = StructuralMapDiv("test_type", divs=[subdiv_1])

    subdiv_2 = StructuralMapDiv("test_type", digital_objects=[digital_object])
    root_div_2 = StructuralMapDiv("test_type", divs=[subdiv_2])

    with pytest.raises(ValueError) as error:
        root_div_1.add_div(root_div_2)
    assert str(error.value) == (
        "Added div contains a digital object that already exists in the div "
        "tree."
    )


def test_nested_digital_objects():
    """Test that all nested digital objects are retrievable drom a div.

    Make sure that nested digital objects cache is updated both when one
    digital object is added with a function, and when a div with digital
    objects is added to the div tree.
    """
    # Original div tree
    do_1 = DigitalObject("path/1")
    do_2 = DigitalObject("path/2")
    do_3 = DigitalObject("path/3")

    subsubdiv = StructuralMapDiv("test_type", digital_objects=[do_3])
    subdiv = StructuralMapDiv(
        "test_type", divs=[subsubdiv], digital_objects=[do_2]
    )
    root_div = StructuralMapDiv(
        "test_type", divs=[subdiv], digital_objects=[do_1]
    )

    assert root_div.nested_digital_objects == {do_1, do_2, do_3}
    assert subdiv.nested_digital_objects == {do_2, do_3}
    assert subsubdiv.nested_digital_objects == {do_3}

    # Div tree with digital objects added
    do_4 = DigitalObject("path/4")
    do_5 = DigitalObject("path/5")

    subdiv_2 = StructuralMapDiv("test_type")
    root_div_2 = StructuralMapDiv("test_type", divs=[subdiv_2])
    root_div_2.add_digital_object(do_4)
    subdiv_2.add_digital_object(do_5)

    subdiv.add_div(root_div_2)

    assert root_div.nested_digital_objects == {do_1, do_2, do_3, do_4, do_5}
    assert subdiv.nested_digital_objects == {do_2, do_3, do_4, do_5}
    assert subsubdiv.nested_digital_objects == {do_3}
    assert root_div_2.nested_digital_objects == {do_4, do_5}
    assert subdiv_2.nested_digital_objects == {do_5}
