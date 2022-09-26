"""Tests for mets.py."""
import pytest

from mets_builder import metadata
from mets_builder.mets import METS, AgentRole, AgentType


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
        "'invalid' is not a valid value for mets_profile. "
        "Value must be one of "
        "['https://digitalpreservation.fi/mets-profiles/cultural-heritage', "
        "'https://digitalpreservation.fi/mets-profiles/research-data']"
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
            mets_profile=(
                "https://digitalpreservation.fi/mets-profiles/"
                "cultural-heritage"
            ),
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
            mets_profile=(
                "https://digitalpreservation.fi/mets-profiles/"
                "cultural-heritage"
            ),
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
            mets_profile=(
                "https://digitalpreservation.fi/mets-profiles/"
                "cultural-heritage"
            ),
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
            mets_profile=(
                "https://digitalpreservation.fi/mets-profiles/"
                "cultural-heritage"
            ),
            package_id="package_id",
            contract_id="contract_id",
            creator_name="Mr. Foo",
            record_status="invalid"
        )
    assert str(error.value) == (
        "'invalid' is not a valid value for record_status. Value must be one "
        "of ['submission', 'update', 'dissemination']"
    )


def test_no_specification_or_catalog_version():
    """Test that initializing METS instance with no specification or
    catalog_version raises ValueError.
    """
    with pytest.raises(ValueError) as error:
        METS(
            mets_profile=(
                "https://digitalpreservation.fi/mets-profiles/"
                "cultural-heritage"
            ),
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
        mets_profile=(
            "https://digitalpreservation.fi/mets-profiles/"
            "cultural-heritage"
        ),
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
        mets_profile=(
            "https://digitalpreservation.fi/mets-profiles/"
            "cultural-heritage"
        ),
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
        mets_profile=(
            "https://digitalpreservation.fi/mets-profiles/"
            "cultural-heritage"
        ),
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


def test_add_metadata():
    """Test adding metadata to METS object."""
    mets = METS(
        mets_profile=(
            "https://digitalpreservation.fi/mets-profiles/"
            "cultural-heritage"
        ),
        package_id="package_id",
        contract_id="contract_id",
        creator_name="Mr. Foo"
    )

    data = metadata.MetadataBase(
        metadata_type="technical",
        metadata_format="PREMIS:OBJECT",
        format_version="1.0"
    )

    mets.add_metadata(data)
    assert mets.metadata == {data}


def test_serialization():
    """Test serializing METS object.

    More thorough testing should be done in serialize module tests.
    """
    mets = METS(
        mets_profile=(
            "https://digitalpreservation.fi/mets-profiles/"
            "cultural-heritage"
        ),
        package_id="package_id",
        contract_id="contract_id",
        creator_name="Mr. Foo"
    )

    result = mets.serialize()

    # bytes.index raises ValueError if subsection is not found
    result.index(b"package_id")
    result.index(b"contract_id")
    result.index(b"Mr. Foo")
