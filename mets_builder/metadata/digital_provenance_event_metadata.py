"""Module for DigitalProvenanceEventMetadata class."""
import uuid
from typing import Optional, List

import premis
from lxml import etree

from mets_builder.metadata import (DigitalProvenanceAgentMetadata,
                                   MetadataBase, MetadataFormat, MetadataType)


class _LinkedAgent:
    """Class holding information of a agent linked to an event."""

    def __init__(
        self,
        agent: DigitalProvenanceAgentMetadata,
        agent_role: str
    ):
        """Constructor for _LinkedAgent."""
        self.agent = agent
        self.agent_role = agent_role


class DigitalProvenanceEventMetadata(MetadataBase):
    """Class for creating digital provenance event metadata.

    The Event entity aggregates information about an action that involves one
    or more digital objects.
    """
    METADATA_TYPE = MetadataType.DIGITAL_PROVENANCE
    METADATA_FORMAT = MetadataFormat.PREMIS_EVENT
    METADATA_FORMAT_VERSION = "2.3"

    def __init__(
        self,
        event_type: str,
        event_datetime: str,
        event_detail: str,
        event_outcome: str,
        event_outcome_detail: str,
        event_identifier_type: Optional[str] = None,
        event_identifier: Optional[str] = None,
        **kwargs
    ) -> None:
        """Constructor for DigitalProvenanceEventMetadata class.

        For advanced configurations keyword arguments for MetadataBase class
        can be given here as well. Look MetadataBase documentation for more
        information.

        :param event_type: A categorization of the nature of the event.
        :param event_datetime: The single date and time, or date and time
            range, at or during which the event occurred.
        :param event_detail: Additional information about the event.
        :param event_outcome: A categorization of the overall result of the
            event in terms of success, partial success, or failure.
        :param event_outcome_detail: A detailed description of the result or
            product of the event.
        :param event_identifier_type: Type of event identifier.
        :param event_identifier: The event identifier value. If not given by
            the user, event identifier is generated automatically.
        """
        self.event_type = event_type
        self.event_datetime = event_datetime
        self.event_detail = event_detail
        self.event_outcome = event_outcome
        self.event_outcome_detail = event_outcome_detail
        self._set_event_identifier_and_type(
            event_identifier_type, event_identifier
        )

        self.linked_agents: List[_LinkedAgent] = []

        super().__init__(
            metadata_type=self.METADATA_TYPE,
            metadata_format=self.METADATA_FORMAT,
            format_version=self.METADATA_FORMAT_VERSION,
            **kwargs
        )

    def link_agent(
        self,
        agent: DigitalProvenanceAgentMetadata,
        agent_role: str
    ) -> None:
        """Link a digital provenance agent to this event.

        :param agent: The agent that is associated with this event.
        :param agent_role: The role of the agent in relation to this event.
        """
        linked_agent = _LinkedAgent(agent=agent, agent_role=agent_role)
        self.linked_agents.append(linked_agent)

    def _set_event_identifier_and_type(self, identifier_type, identifier):
        """Resolve event identifier and identifier type.

        If identifier is given, also identifier type must be declared by the
        user. If identifier is not given by the user, event identifier should
        be generated.
        """
        if identifier and not identifier_type:
            raise ValueError(
                "Event identifier type is not given, but event identifier is."
            )

        if not identifier:
            identifier_type = "UUID"
            identifier = str(uuid.uuid4())

        self.event_identifier_type = identifier_type
        self.event_identifier = identifier

    def _serialize_linked_agents_to_xml_elements(self):
        """Serialize linked agents to XML elements."""
        linked_agent_ids = [
            premis.identifier(
                identifier_type=linked_agent.agent.agent_identifier_type,
                identifier_value=linked_agent.agent.agent_identifier,
                prefix='linkingAgent',
                role=linked_agent.agent_role
            )
            for linked_agent in self.linked_agents
        ]
        return linked_agent_ids

    def to_xml_element_tree(self) -> etree._Element:
        """Serialize this metadata object to XML using lxml elements.

        :returns: The root element of the metadata serialized into XML.
        """
        event_id = premis.identifier(
            identifier_type=self.event_identifier_type,
            identifier_value=self.event_identifier,
            prefix="event"
        )

        outcome = premis.outcome(
            outcome=self.event_outcome,
            detail_note=self.event_outcome_detail
        )

        linked_agents = self._serialize_linked_agents_to_xml_elements()

        event_child_elements = [outcome] + linked_agents

        event = premis.event(
            event_id=event_id,
            event_type=self.event_type,
            event_date_time=self.event_datetime,
            event_detail=self.event_detail,
            child_elements=event_child_elements
        )

        return event
