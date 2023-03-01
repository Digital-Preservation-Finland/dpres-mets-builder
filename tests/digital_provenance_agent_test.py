"""Tests for digital provenange agent metadata."""
from pathlib import Path

import pytest
import xml_helpers.utils

from mets_builder.metadata import DigitalProvenanceAgentMetadata
from mets_builder.serialize import _NAMESPACES


def test_invalid_agent_type():
    """Test that aproviding invalid agent type raises an error."""
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
