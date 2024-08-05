"""Tests for structural map classes."""
import pytest

from mets_builder.digital_object import DigitalObject
import mets_builder.metadata
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


def test_add_divs_to_div():
    """Test adding divisions to a structural map division."""
    div = StructuralMapDiv(div_type="test_type")
    assert div.divs == set()

    nested_div_1 = StructuralMapDiv(div_type="test_type")
    nested_div_2 = StructuralMapDiv(div_type="test_type")
    div.add_divs([nested_div_1, nested_div_2])
    assert div.divs == {nested_div_1, nested_div_2}


def test_add_metadata_to_div():
    """Test adding metadata to a structural map division."""
    div = StructuralMapDiv(div_type="test_type")
    assert div.metadata == set()

    metadata = mets_builder.metadata.ImportedMetadata(
        data_string="<root><sub1></sub1><sub2></sub2></root>",
        metadata_type=mets_builder.metadata.MetadataType.DESCRIPTIVE,
        metadata_format=mets_builder.metadata.MetadataFormat.OTHER,
        other_format="PAS-special",
        format_version="1.0",
    )
    div.add_metadata(metadata)
    assert div.metadata == {metadata}


def test_add_linked_metadata_to_div():
    """Test adding metadata with linked metadata."""
    div = StructuralMapDiv(div_type="test_type")
    assert div.metadata == set()

    # Create event metadata and agent metadata
    event = mets_builder.metadata.DigitalProvenanceEventMetadata(
        event_type="foo",
        event_detail="bar",
        event_outcome="success",
        event_outcome_detail="baz",
    )
    agent = mets_builder.metadata.DigitalProvenanceAgentMetadata(
        agent_name="cowsay",
        agent_type="software",
    )

    # Link agent metadata to event metadata
    event.link_agent_metadata(
        agent_metadata=agent,
        agent_role="creator"
    )

    # The agent metadata should be automatically added to div
    div.add_metadata(event)
    assert div.metadata == {event, agent}


def test_add_digital_objects_to_div():
    """Test adding digital objects to a structural map division."""
    div = StructuralMapDiv(div_type="test_type")
    assert div.digital_objects == set()

    digital_object_1 = DigitalObject(path="path/1")
    digital_object_2 = DigitalObject(path="path/2")
    div.add_digital_objects([digital_object_1, digital_object_2])
    assert div.digital_objects == {digital_object_1, digital_object_2}


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
        root_div.add_divs([root_div])

    # Add a div that already exists lower in tree
    with pytest.raises(ValueError):
        root_div.add_divs([subsubdiv])

    # Add a div that already exists higher up in the tree
    with pytest.raises(ValueError):
        subsubdiv.add_divs([root_div])

    # Add a div that lower in its tree contains a div that already exists in
    # the parent div tree
    new_div = StructuralMapDiv("test_type", divs=[root_div])
    with pytest.raises(ValueError):
        subdiv.add_divs([new_div])

    # Add a div to its sibling
    subsubdiv_sibling = StructuralMapDiv("test_type")
    subdiv.add_divs([subsubdiv_sibling])
    with pytest.raises(ValueError):
        subsubdiv.add_divs([subsubdiv_sibling])


def test_add_duplicate_object_to_div():
    """Test that adding a digital object twice to a div raises an error."""
    subsubdiv = StructuralMapDiv("test_type")
    subdiv = StructuralMapDiv("test_type", divs=[subsubdiv])
    root_div = StructuralMapDiv("test_type", divs=[subdiv])

    digital_object = DigitalObject("path")
    subdiv.add_digital_objects([digital_object])

    # Adding the object second time to the same div
    with pytest.raises(ValueError):
        subdiv.add_digital_objects([digital_object])

    # Adding the object to parent div
    with pytest.raises(ValueError):
        root_div.add_digital_objects([digital_object])

    # Adding the object to child div
    with pytest.raises(ValueError):
        subsubdiv.add_digital_objects([digital_object])

    # Adding the object to a sibling
    subdiv_sibling = StructuralMapDiv("test_type")
    root_div.add_divs([subdiv_sibling])
    with pytest.raises(ValueError):
        subdiv_sibling.add_digital_objects([digital_object])


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
        root_div_1.add_divs([root_div_2])
    assert str(error.value) == (
        "An added div contains a digital object that already exists in the "
        "div tree."
    )


def test_nested_digital_objects():
    """Test that all nested digital objects are retrievable from a div.

    Make sure that nested digital objects stay correct both when a digital
    object is added with a function, and when a div with digital objects is
    added to the div tree.
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
    root_div_2.add_digital_objects([do_4])
    subdiv_2.add_digital_objects([do_5])

    subdiv.add_divs([root_div_2])

    assert root_div.nested_digital_objects == {do_1, do_2, do_3, do_4, do_5}
    assert subdiv.nested_digital_objects == {do_2, do_3, do_4, do_5}
    assert subsubdiv.nested_digital_objects == {do_3}
    assert root_div_2.nested_digital_objects == {do_4, do_5}
    assert subdiv_2.nested_digital_objects == {do_5}


def test_add_single_div_as_multiple_divs():
    """Test that trying to pass one div as an iterable of divs to function that
    adds multiple divs to a div raises an error.
    """
    root_div = StructuralMapDiv("test_type")
    added_div = StructuralMapDiv("test_type")

    with pytest.raises(TypeError) as error:
        root_div.add_divs(added_div)

    assert str(error.value) == (
        "Given 'divs' is a single StructuralMapDiv. Give an iterable of "
        "StructuralMapDivs as the 'divs' argument."
    )


def test_add_div_with_parent_to_a_div():
    """Test that adding a div that already has a parent div to a div raises an
    error.
    """
    root_div = StructuralMapDiv("test_type")

    div_with_parent = StructuralMapDiv("test_type")
    StructuralMapDiv("test_type", divs=[div_with_parent])

    with pytest.raises(ValueError) as error:
        root_div.add_divs([div_with_parent])

    assert str(error.value) == "An added div is already has a parent div."


def test_structural_map_div_metadata_bundling():
    """Test that shared metadata is bundled as close to the root div as
    possible.
    """
    shared_event = mets_builder.metadata.DigitalProvenanceEventMetadata(
        event_type="shared",
        event_detail="bar",
        event_outcome="success",
        event_outcome_detail="baz",
    )
    shared_agent = mets_builder.metadata.DigitalProvenanceAgentMetadata(
        agent_name="shared",
        agent_type="software",
    )
    unshared_event = mets_builder.metadata.DigitalProvenanceEventMetadata(
        event_type="unshared",
        event_detail="bar",
        event_outcome="success",
        event_outcome_detail="baz",
    )
    unshared_agent = mets_builder.metadata.DigitalProvenanceAgentMetadata(
        agent_name="unshared",
        agent_type="software",
    )
    partly_shared_event = mets_builder.metadata.DigitalProvenanceEventMetadata(
        event_type="partly_shared",
        event_detail="bar",
        event_outcome="success",
        event_outcome_detail="baz",
    )
    partly_shared_agent = mets_builder.metadata.DigitalProvenanceAgentMetadata(
        agent_name="partly_shared",
        agent_type="software",
    )

    do_1 = DigitalObject("path/1")
    do_2 = DigitalObject("path/2")
    do_3 = DigitalObject("path/3")
    do_4 = DigitalObject("path/4")
    do_5 = DigitalObject("path/5")
    do_6 = DigitalObject("path/6")

    dos = [do_1, do_2, do_3, do_4, do_5, do_6]

    do_2.add_metadata(unshared_event)
    do_2.add_metadata(unshared_agent)

    do_5.add_metadata(partly_shared_event)
    do_5.add_metadata(partly_shared_agent)

    do_6.add_metadata(partly_shared_event)
    do_6.add_metadata(partly_shared_agent)

    for do in dos:
        do.add_metadata(shared_event)
        do.add_metadata(shared_agent)

    root_div = StructuralMapDiv("test_type")
    div1 = StructuralMapDiv("test_type")
    div2 = StructuralMapDiv("test_type")
    div3 = StructuralMapDiv("test_type")

    divs = [root_div, div1, div2, div3]

    root_div.add_divs([div1, div2])
    root_div.add_digital_objects([do_1])

    div1.add_digital_objects([do_2, do_3])

    div2.add_divs([div3])
    div2.add_digital_objects([do_4])

    div3.add_digital_objects([do_5, do_6])

    root_div.bundle_metadata()

    do_metadata = [metadata for do in dos for metadata in do.metadata]
    div_metadata = [metadata for div in divs for metadata in div.metadata]

    assert unshared_event not in div_metadata
    assert unshared_agent not in div_metadata

    assert partly_shared_event not in do_metadata
    assert partly_shared_agent not in do_metadata

    assert partly_shared_event in div3.metadata
    assert partly_shared_agent in div3.metadata

    assert shared_event not in do_metadata
    assert shared_event in root_div.metadata

    assert shared_agent not in do_metadata
    assert shared_agent in root_div.metadata
