"""Tests for digital provenance agent metadata."""
from pathlib import Path

import pytest
import xml_helpers.utils

from mets_builder.metadata import DigitalProvenanceAgentMetadata
from mets_builder.serialize import _NAMESPACES


def test_invalid_agent_type():
    """Test that providing invalid agent type raises an error."""
    with pytest.raises(ValueError):
        DigitalProvenanceAgentMetadata(
            agent_identifier_type="agent-identifier-type",
            agent_identifier="agent-identifier-value",
            agent_name="agent-name",
            agent_type="invalid-agent",
        )


def test_serialization():
    """Test serializing the digital provenance agent object."""
    data = DigitalProvenanceAgentMetadata(
        agent_identifier_type="agent-identifier-type",
        agent_identifier="agent-identifier-value",
        agent_name="agent-name",
        agent_type="organization",
        agent_note="agent-note"
    )

    result = xml_helpers.utils.serialize(
        data.to_xml_element_tree()
    ).decode("utf-8")

    expected_xml = Path(
        "tests/data/expected_digital_provenance_agent_metadata.xml"
    ).read_text(encoding="utf-8")

    assert result == expected_xml


@pytest.mark.parametrize(
    ["agent_type", "expected_name"],
    [
        ("software", "agent-name-v1.0"),
        ("hardware", "agent-name-v1.0"),
        ("organization", "agent-name"),
        ("person", "agent-name")
    ]
)
def test_serialized_agent_version(agent_type, expected_name):
    """Test that agent version is appended to the agent name when applicable.
    """
    data = DigitalProvenanceAgentMetadata(
        agent_identifier_type="agent-identifier-type",
        agent_identifier="agent-identifier-value",
        agent_name="agent-name",
        agent_type=agent_type,
        agent_version="1.0"
    )

    result = data.to_xml_element_tree()
    name_element = result.find("premis:agentName", namespaces=_NAMESPACES)
    assert name_element.text == expected_name


def test_identifier_type_not_set():
    """Test that an error is raised if agent identifier type is not given along
    with an identifier.
    """
    with pytest.raises(ValueError) as error:
        DigitalProvenanceAgentMetadata(
            agent_identifier_type=None,
            agent_identifier="agent-identifier-value",
            agent_name="agent-name",
            agent_type="organization"
        )
    assert str(error.value) == (
        "Agent identifier type is not given, but agent identifier is."
    )


def test_generate_agent_identifier():
    """Test that agent identifier is generated and type set to 'local', if
    identifier is not given by the user.
    """
    agent = DigitalProvenanceAgentMetadata(
        agent_identifier_type=None,
        agent_identifier=None,
        agent_name="agent-name",
        agent_type="software",
        agent_version="1.0"
    )
    assert agent.agent_identifier_type == "local"
    assert agent.agent_identifier


def test_user_given_identifier():
    """Test that user gan give agent identifier and type."""
    agent = DigitalProvenanceAgentMetadata(
        agent_identifier_type="user-type",
        agent_identifier="user-identifier",
        agent_name="agent-name",
        agent_type="software",
        agent_version="1.0"
    )
    assert agent.agent_identifier_type == "user-type"
    assert agent.agent_identifier == "user-identifier"
