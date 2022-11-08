"""Tests for mets.py."""
from pathlib import Path

import pytest

from mets_builder import metadata
from mets_builder.digital_object import DigitalObject, DigitalObjectStream
from mets_builder.file_references import FileReferences
from mets_builder.mets import METS, AgentRole, AgentType, MetsProfile
from mets_builder.structural_map import StructuralMap, StructuralMapDiv


def test_invalid_mets_profile():
    """Test that initializing METS instance with invalid METS profile raises
    ValueError.
    """
    with pytest.raises(ValueError) as error:
        METS(
            mets_profile="invalid",
            package_id="package_id",
            contract_id="contract_id",
            creator_name="Mr. Foo"
        )
    assert str(error.value) == (
        "'invalid' is not a valid MetsProfile"
    )


@pytest.mark.parametrize(
    ["invalid_value", "error_message"],
    [
        ("", "package_id cannot be empty"),
        ("ä", ("package_id 'ä' contains characters that are not printable "
               "US-ASCII characters"))
    ]
)
def test_invalid_package_id(invalid_value, error_message):
    """Test that initializing METS instance with invalid package_id raises
    ValueError.
    """
    with pytest.raises(ValueError) as error:
        METS(
            mets_profile=MetsProfile.CULTURAL_HERITAGE,
            package_id=invalid_value,
            contract_id="contract_id",
            creator_name="Mr. Foo"
        )
    assert str(error.value) == error_message


@pytest.mark.parametrize(
    ["invalid_value", "error_message"],
    [
        (None, "contract_id can not be None"),
        ("ä", ("contract_id 'ä' contains characters that are not printable "
               "US-ASCII characters"))
    ]
)
def test_invalid_contract_id(invalid_value, error_message):
    """Test that initializing METS instance with invalid contract_id raises
    ValueError.
    """
    with pytest.raises(ValueError) as error:
        METS(
            mets_profile=MetsProfile.CULTURAL_HERITAGE,
            package_id="package_id",
            contract_id=invalid_value,
            creator_name="Mr. Foo"
        )
    assert str(error.value) == error_message


def test_invalid_content_id():
    """Test that initializing METS instance with invalid content_id raises
    ValueError.
    """
    with pytest.raises(ValueError) as error:
        METS(
            mets_profile=MetsProfile.CULTURAL_HERITAGE,
            package_id="package_id",
            contract_id="contract_id",
            creator_name="Mr. Foo",
            content_id="ä"
        )
    assert str(error.value) == (
        "content_id 'ä' contains characters that are not printable US-ASCII "
        "characters"
    )


def test_invalid_record_status():
    """Test that initializing METS instance with invalid record_status raises
    ValueError.
    """
    with pytest.raises(ValueError) as error:
        METS(
            mets_profile=MetsProfile.CULTURAL_HERITAGE,
            package_id="package_id",
            contract_id="contract_id",
            creator_name="Mr. Foo",
            record_status="invalid"
        )
    assert str(error.value) == "'invalid' is not a valid MetsRecordStatus"


def test_no_specification_or_catalog_version():
    """Test that initializing METS instance with no specification or
    catalog_version raises ValueError.
    """
    with pytest.raises(ValueError) as error:
        METS(
            mets_profile=MetsProfile.CULTURAL_HERITAGE,
            package_id="package_id",
            contract_id="contract_id",
            creator_name="Mr. Foo",
            catalog_version=None,
            specification=None
        )
    assert str(error.value) == (
        "Either catalog_version or specification has to be set"
    )


def test_add_agent():
    """Test that agent can be added to a METS object."""
    mets = METS(
        mets_profile=MetsProfile.CULTURAL_HERITAGE,
        package_id="package_id",
        contract_id="contract_id",
        creator_name="Mr. Foo"
    )
    mets.add_agent(name="name", agent_role="EDITOR", agent_type="INDIVIDUAL")

    # Creator agent has been added on initialization, so there should be two
    # agents
    assert len(mets.agents) == 2

    # role and type are casted to their enum types
    assert mets.agents[1].agent_role == AgentRole.EDITOR
    assert mets.agents[1].agent_type == AgentType.INDIVIDUAL

    assert mets.agents[1].name == "name"


@pytest.mark.parametrize(
    ["agent_role", "other_role", "agent_type", "other_type"],
    [
        # Invalid role
        ("invalid", None, "ORGANIZATION", None),
        # role is OTHER but other_role is not set
        ("OTHER", None, "ORGANIZATION", None),
        # No role or other_role
        (None, None, "ORGANIZATION", None),
        # Invalid type
        ("CREATOR", None, "invalid", None),
        # type is OTHER but other_type is not set
        ("CREATOR", None, "OTHER", None),
        # No type or other_type
        ("CREATOR", None, None, None)
    ]
)
def test_add_agent_invalid_arguments(
    agent_role, other_role, agent_type, other_type
):
    """Test adding agents with invalid roles and types."""
    mets = METS(
        mets_profile=MetsProfile.CULTURAL_HERITAGE,
        package_id="package_id",
        contract_id="contract_id",
        creator_name="Mr. Foo"
    )

    with pytest.raises(ValueError):
        mets.add_agent(
            name="name",
            agent_role=agent_role,
            other_role=other_role,
            agent_type=agent_type,
            other_type=other_type
        )


def test_add_agent_with_other_role_and_type():
    """Test giving other_role or other_type to agent overrides role and type
    values.
    """
    mets = METS(
        mets_profile=MetsProfile.CULTURAL_HERITAGE,
        package_id="package_id",
        contract_id="contract_id",
        creator_name="Mr. Foo"
    )
    mets.add_agent(
        name="name",
        agent_role="CREATOR",
        other_role="other_role",
        agent_type="INDIVIDUAL",
        other_type="other_type"
    )

    assert mets.agents[1].agent_role == AgentRole.OTHER
    assert mets.agents[1].other_role == "other_role"
    assert mets.agents[1].agent_type == AgentType.OTHER
    assert mets.agents[1].other_type == "other_type"

    assert mets.agents[1].name == "name"


def test_get_metadata():
    """Test getting metadata added to a METS object through digital objects and
    multiple structural maps with nested divs.
    """
    mets = METS(
        mets_profile=MetsProfile.CULTURAL_HERITAGE,
        package_id="package_id",
        contract_id="contract_id",
        creator_name="Mr. Foo"
    )
    md_stream = metadata.ImportedMetadata(
        data_path=Path("tests/data/imported_metadata.xml"),
        metadata_type="technical",
        metadata_format="other",
        other_format="PAS-special",
        format_version="1.0"
    )
    md_digital_object = metadata.ImportedMetadata(
        data_path=Path("tests/data/imported_metadata.xml"),
        metadata_type="technical",
        metadata_format="other",
        other_format="PAS-special",
        format_version="1.0"
    )
    md_structural_map_1 = metadata.ImportedMetadata(
        data_path=Path("tests/data/imported_metadata.xml"),
        metadata_type="descriptive",
        metadata_format="other",
        other_format="PAS-special",
        format_version="1.0"
    )
    md_structural_map_2 = metadata.ImportedMetadata(
        data_path=Path("tests/data/imported_metadata.xml"),
        metadata_type="descriptive",
        metadata_format="other",
        other_format="PAS-special",
        format_version="1.0"
    )
    expected_metadata = {
        md_stream, md_digital_object, md_structural_map_1, md_structural_map_2
    }

    stream = DigitalObjectStream(metadata=[md_stream])
    digital_object = DigitalObject(
        path_in_sip="path",
        streams=[stream],
        metadata=[md_digital_object]
    )

    #  two structural maps, one with metadata in a nested div
    root_div_1 = StructuralMapDiv(
        div_type="test_type",
        digital_objects=[digital_object],
        metadata=[md_structural_map_1]
    )
    structural_map_1 = StructuralMap(root_div=root_div_1)
    mets.add_structural_map(structural_map_1)

    subdiv = StructuralMapDiv(
        div_type="test_type",
        digital_objects=[digital_object],
        metadata=[md_structural_map_2]
    )
    root_div_2 = StructuralMapDiv(
        div_type="test_type",
        divs=[subdiv]
    )
    structural_map_2 = StructuralMap(root_div=root_div_2)
    mets.add_structural_map(structural_map_2)

    assert mets.metadata == expected_metadata


def test_get_digital_objects():
    """Test getting the digital objects that have been added to a METS object
    via structural maps.
    """
    mets = METS(
        mets_profile=MetsProfile.CULTURAL_HERITAGE,
        package_id="package_id",
        contract_id="contract_id",
        creator_name="Mr. Foo"
    )

    subdiv_digital_objects = {
        DigitalObject(path_in_sip="path/1"),
        DigitalObject(path_in_sip="path/2"),
        DigitalObject(path_in_sip="path/3")
    }
    root_div_digital_objects = {
        DigitalObject(path_in_sip="path/1"),
        DigitalObject(path_in_sip="path/2"),
        DigitalObject(path_in_sip="path/3")
    }
    all_digital_objects = subdiv_digital_objects | root_div_digital_objects

    subdiv = StructuralMapDiv(
        "test_type",  digital_objects=subdiv_digital_objects
    )
    root_div = StructuralMapDiv(
        "test_type", digital_objects=root_div_digital_objects, divs=[subdiv]
    )
    structural_map = StructuralMap(root_div=root_div)
    mets.add_structural_map(structural_map)

    assert mets.digital_objects == all_digital_objects


def test_add_file_references():
    """Test adding file references to METS object."""
    mets = METS(
        mets_profile=MetsProfile.CULTURAL_HERITAGE,
        package_id="package_id",
        contract_id="contract_id",
        creator_name="Mr. Foo"
    )

    assert mets.file_references is None
    file_references = FileReferences()
    mets.add_file_references(file_references)
    assert mets.file_references == file_references


def test_generating_file_references():
    """Test generating file references for METS object."""
    mets = METS(
        mets_profile=MetsProfile.CULTURAL_HERITAGE,
        package_id="package_id",
        contract_id="contract_id",
        creator_name="Mr. Foo"
    )

    digital_objects = {
        DigitalObject(path_in_sip="path/1"),
        DigitalObject(path_in_sip="path/2"),
        DigitalObject(path_in_sip="path/3")
    }

    root_div = StructuralMapDiv("test_type", digital_objects=digital_objects)
    structural_map = StructuralMap(root_div=root_div)
    mets.add_structural_map(structural_map)

    assert mets.file_references is None
    mets.generate_file_references()
    assert mets.file_references

    assert len(mets.file_references.file_groups) == 1
    group = mets.file_references.file_groups.pop()
    assert group.digital_objects == digital_objects


def test_adding_structural_map():
    """Test adding a structural map to METS object."""
    mets = METS(
        mets_profile=MetsProfile.CULTURAL_HERITAGE,
        package_id="package_id",
        contract_id="contract_id",
        creator_name="Mr. Foo"
    )
    root_div = StructuralMapDiv(div_type="test_type")
    structural_map_1 = StructuralMap(root_div=root_div)
    structural_map_2 = StructuralMap(root_div=root_div)

    assert mets.structural_maps == set()
    mets.add_structural_map(structural_map_1)
    assert mets.structural_maps == {structural_map_1}
    mets.add_structural_map(structural_map_2)
    assert mets.structural_maps == {structural_map_1, structural_map_2}


def test_mets_to_xml():
    """Test serializing METS object to XML string.

    More thorough testing should be done in serialize module tests.
    """
    mets = METS(
        mets_profile=MetsProfile.CULTURAL_HERITAGE,
        package_id="package_id",
        contract_id="contract_id",
        creator_name="Mr. Foo"
    )

    result = mets.to_xml()

    # bytes.index raises ValueError if subsection is not found
    result.index(b"package_id")
    result.index(b"contract_id")
    result.index(b"Mr. Foo")
