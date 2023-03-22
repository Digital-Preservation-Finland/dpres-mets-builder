"""Tests for digital provenance event metadata."""
from pathlib import Path

import pytest
import xml_helpers.utils

from mets_builder.metadata import (DigitalProvenanceAgentMetadata,
                                   DigitalProvenanceEventMetadata,
                                   TechnicalObjectMetadata)


def test_serialization():
    """Test serializing the digital provenance event object."""
    event = DigitalProvenanceEventMetadata(
        event_type="event-type",
        event_datetime="2000-01-01T10:11:12",
        event_detail="event-detail",
        event_outcome="success",
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

    object_1 = TechnicalObjectMetadata(
        file_format="file-format",
        file_format_version="file-format-version",
        checksum_algorithm="MD5",
        checksum="checksum",
        file_created_date="2000-01-01T00:00:00",
        object_identifier_type="test-type",
        object_identifier="object-1"
    )
    object_2 = TechnicalObjectMetadata(
        file_format="file-format",
        file_format_version="file-format-version",
        checksum_algorithm="MD5",
        checksum="checksum",
        file_created_date="2000-01-01T00:00:00",
        object_identifier_type="test-type",
        object_identifier="object-2"
    )
    event.link_object_metadata(object_1, object_role="object-role-1")
    event.link_object_metadata(object_2, object_role="object-role-2")

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
            event_outcome="success",
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
        event_outcome="success",
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
        event_outcome="success",
        event_outcome_detail="event-outcome-detail",
        event_identifier_type="user-type",
        event_identifier="user-identifier"
    )
    assert event.event_identifier_type == "user-type"
    assert event.event_identifier == "user-identifier"


@pytest.mark.parametrize(
    "event_outcome",
    (
        "success",
        "failure",
        "(:unac)",
        "(:unal)",
        "(:unap)",
        "(:unav)",
        "(:unkn)",
        "(:none)",
        "(:null)",
        "(:tba)",
        "(:etal)"
    )
)
def test_valid_event_outcomes(event_outcome):
    """Test that valid event outcomes can be set."""
    event = DigitalProvenanceEventMetadata(
        event_type="event-type",
        event_datetime="2000-01-01T10:11:12",
        event_detail="event-detail",
        event_outcome=event_outcome,
        event_outcome_detail="event-outcome-detail"
    )
    assert event.event_outcome.value == event_outcome


@pytest.mark.parametrize(
    "invalid_event_outcome",
    (
        (""),
        (None),
        ("invalid-event-outcome")
    )
)
def test_invalid_event_outcomes(invalid_event_outcome):
    """Test that invalid event outcomes raise an error."""
    event = DigitalProvenanceEventMetadata(
        event_type="event-type",
        event_datetime="2000-01-01T10:11:12",
        event_detail="event-detail",
        event_outcome="success",
        event_outcome_detail="event-outcome-detail"
    )
    with pytest.raises(ValueError):
        event.event_outcome = invalid_event_outcome
