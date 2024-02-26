"""Tests for structural map classes."""
from uuid import UUID

import pytest

from mets_builder.digital_object import DigitalObject
from mets_builder.metadata import (DigitalProvenanceAgentMetadata,
                                   DigitalProvenanceEventMetadata,
                                   MetadataBase, MetadataFormat, MetadataType)
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

    metadata = MetadataBase(
        metadata_type=MetadataType.DESCRIPTIVE,
        metadata_format=MetadataFormat.OTHER,
        other_format="PAS-special",
        format_version="1.0"
    )
    div.add_metadata(metadata)
    assert div.metadata == {metadata}


def test_add_digital_objects_to_div():
    """Test adding digital objects to a structural map division."""
    div = StructuralMapDiv(div_type="test_type")
    assert div.digital_objects == set()

    digital_object_1 = DigitalObject(sip_filepath="path/1")
    digital_object_2 = DigitalObject(sip_filepath="path/2")
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
    """Test that all nested digital objects are retrievable drom a div.

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


def test_generating_structural_map_from_directory():
    """Test generating structural map from directory contents.

    There should be a div for each directory, and the divs should be nested
    according to the directory structure. The type of each div should be the
    corresponding directory name. The file is not represented with a div, but
    as a DigitalObject stored in the correct div.

    The root div should be an additional wrapping div with type 'directory'.
    """
    do1 = DigitalObject(sip_filepath="data/a/file1.txt")
    do2 = DigitalObject(sip_filepath="data/a/file2.txt")
    do3 = DigitalObject(sip_filepath="data/b/deep/directory/chain/file3.txt")
    digital_objects = (do1, do2, do3)

    structural_map = StructuralMap.from_directory_structure(digital_objects)

    assert structural_map.structural_map_type is None

    # defined directory structure is wrapped in a root div with type
    # "directory"
    root_div = structural_map.root_div
    assert root_div.div_type == "directory"
    assert len(root_div.divs) == 1

    # root of the user defined tree is a directory called "data", containing
    # two other directories
    data_div = root_div.divs.pop()
    assert data_div.div_type == "data"
    assert len(data_div.divs) == 2

    # directory "a" in "data" contains digital objects 1 and 2
    a_div = next(div for div in data_div if div.div_type == "a")
    assert a_div.digital_objects == {do1, do2}

    # directory "b" in "data" has a deep directory structure, at the bottom of
    # which is digital object 3
    b_div = next(div for div in data_div if div.div_type == "b")
    deep_div = b_div.divs.pop()
    assert deep_div.div_type == "deep"
    directory_div = deep_div.divs.pop()
    assert directory_div.div_type == "directory"
    chain_div = directory_div.divs.pop()
    assert chain_div.div_type == "chain"
    assert chain_div.digital_objects == {do3}


def test_generating_structural_map_with_no_digital_objects():
    """Test that generating structural map with zero digital objects raises an
    error.
    """
    with pytest.raises(ValueError) as error:
        StructuralMap.from_directory_structure([])
    assert str(error.value) == (
        "Given 'digital_objects' is empty. Structural map can not be "
        "generated with zero digital objects."
    )


def test_generating_structural_map_digital_provenance():
    """Test that digital provenance metadata is created correctly when
    structural map is generated.

    Event (structmap generation) and agent (dpres-mets-builder) should have
    been added to the root div of the generated structural map. The agent
    should also be linked to the event as the executing program.
    """
    digital_object = DigitalObject(sip_filepath="data/file.txt")
    structural_map = StructuralMap.from_directory_structure([digital_object])

    root_div = structural_map.root_div
    assert len(root_div.metadata) == 2

    # Event
    event = next(
        metadata for metadata in root_div.metadata
        if isinstance(metadata, DigitalProvenanceEventMetadata)
    )
    assert event.event_type == "creation"
    assert event.event_detail == (
        "Creation of structural metadata with the "
        "StructuralMap.from_directory_structure method"
    )
    assert event.event_outcome.value == "success"
    assert event.event_outcome_detail == (
        "Created METS structural map with type 'directory'"
    )
    assert event.event_identifier_type == "UUID"
    # Fails if not a valid UUID v4
    UUID(event.event_identifier, version=4)

    # Agent
    assert len(event.linked_agents) == 1
    linked_agent = event.linked_agents[0]
    assert linked_agent.agent_role == "executing program"
    assert linked_agent.agent_metadata.agent_name == "dpres-mets-builder"

    agent_in_div = next(
        metadata for metadata in root_div.metadata
        if isinstance(metadata, DigitalProvenanceAgentMetadata)
    )
    assert agent_in_div == linked_agent.agent_metadata


def test_generating_structural_map_digital_provenance_with_custom_agents():
    """Test that custom agents can be added to generated structural map.

    The agents should have been added to the root div of the generated
    structural map. The agents should also be linked to the structmap creation
    event as executing programs.
    """
    digital_object = DigitalObject(sip_filepath="data/file.txt")
    custom_agent_1 = DigitalProvenanceAgentMetadata(
        agent_name="custom_agent_1",
        agent_version="1.0",
        agent_type="software"
    )
    custom_agent_2 = DigitalProvenanceAgentMetadata(
        agent_name="custom_agent_2",
        agent_version="1.0",
        agent_type="software"
    )

    structural_map = StructuralMap.from_directory_structure(
        [digital_object],
        additional_agents=[custom_agent_1, custom_agent_2]
    )

    root_div = structural_map.root_div
    mets_builder = DigitalProvenanceAgentMetadata.get_mets_builder_agent()
    assert mets_builder in root_div.metadata
    assert custom_agent_1 in root_div.metadata
    assert custom_agent_2 in root_div.metadata

    event = next(
        metadata for metadata in root_div.metadata
        if isinstance(metadata, DigitalProvenanceEventMetadata)
    )
    linked_agents = (agent.agent_metadata for agent in event.linked_agents)
    assert mets_builder in linked_agents
    assert custom_agent_1 in linked_agents
    assert custom_agent_2 in linked_agents
