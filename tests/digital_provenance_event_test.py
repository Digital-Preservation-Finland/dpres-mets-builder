"""Tests for digital provenance event metadata."""
from pathlib import Path

import pytest
import xml_helpers.utils

from mets_builder.metadata import (DigitalProvenanceAgentMetadata,
                                   DigitalProvenanceEventMetadata)


def test_serialization():
    """Test serializing the digital provenance event object."""
    event = DigitalProvenanceEventMetadata(
        event_type="event-type",
        event_datetime="2000-01-01T10:11:12",
        event_detail="event-detail",
        event_outcome="event-outcome",
        event_outcome_detail="event-outcome-detail",
        event_identifier_type="event-identifier-type",
        event_identifier="event-identifier-value"
    )

    agent_1 = DigitalProvenanceAgentMetadata(
        agent_name="agent-name",
        agent_type="organization",
        agent_identifier_type="test-type",
        agent_identifier="agent-1"
    )
    agent_2 = DigitalProvenanceAgentMetadata(
        agent_name="agent-name",
        agent_type="organization",
        agent_identifier_type="test-type",
        agent_identifier="agent-2"
    )
    event.link_agent(agent_1, agent_role="agent-role-1")
    event.link_agent(agent_2, agent_role="agent-role-2")

    result = xml_helpers.utils.serialize(
        event.to_xml_element_tree()
    ).decode("utf-8")

    expected_xml = Path(
        "tests/data/expected_digital_provenance_event_metadata.xml"
    ).read_text(encoding="utf-8")

    assert result == expected_xml


def test_identifier_type_not_set():
    """Test that an error is raised if event identifier type is not given along
    with an identifier.
    """
    with pytest.raises(ValueError) as error:
        DigitalProvenanceEventMetadata(
            event_type="event-type",
            event_datetime="2000-01-01T10:11:12",
            event_detail="event-detail",
            event_outcome="event-outcome",
            event_outcome_detail="event-outcome-detail",
            event_identifier_type=None,
            event_identifier="event-identifier-value"
        )
    assert str(error.value) == (
        "Event identifier type is not given, but event identifier is."
    )


def test_generate_agent_identifier():
    """Test that event identifier is generated and type set to 'UUID', if
    identifier is not given by the user.
    """
    event = DigitalProvenanceEventMetadata(
        event_type="event-type",
        event_datetime="2000-01-01T10:11:12",
        event_detail="event-detail",
        event_outcome="event-outcome",
        event_outcome_detail="event-outcome-detail",
        event_identifier_type=None,
        event_identifier=None
    )
    assert event.event_identifier_type == "UUID"
    assert event.event_identifier


def test_user_given_identifier():
    """Test that user gan give event identifier and type."""
    event = DigitalProvenanceEventMetadata(
        event_type="event-type",
        event_datetime="2000-01-01T10:11:12",
        event_detail="event-detail",
        event_outcome="event-outcome",
        event_outcome_detail="event-outcome-detail",
        event_identifier_type="user-type",
        event_identifier="user-identifier"
    )
    assert event.event_identifier_type == "user-type"
    assert event.event_identifier == "user-identifier"
