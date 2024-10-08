"""Module for DigitalProvenanceEventMetadata class."""
from enum import Enum
from typing import List, Optional, Union

import premis
from lxml import etree

from mets_builder.metadata import (ComparableMixin,
                                   DigitalProvenanceAgentMetadata,
                                   Metadata, MetadataFormat, MetadataType,
                                   TechnicalObjectMetadata)


class EventOutcome(Enum):
    """Enum for valid event outcomes."""

    SUCCESS = "success"
    """Succesful outcome."""

    FAILURE = "failure"
    """Unsuccesful outcome."""

    UNACCESSIBLE = "(:unac)"
    """Temporarily inaccessible."""

    UNALLOWED = "(:unal)"
    """Unallowed, suppressed intentionally."""

    UNAPPLICABLE = "(:unap)"
    """Not applicable, makes no sense."""

    UNAVAILABLE = "(:unav)"
    """Value unavailable, possibly unknown."""

    UNKNOWN = "(:unkn)"
    """Known to be unknown (e.g., Anonymous, Inconnue)."""

    NONE = "(:none)"
    """Never had a value, never will."""

    NULL = "(:null)"
    """Explicitly and meaningfully empty."""

    TO_BE_ANNOUNCED = "(:tba)"
    """To be assigned or announced later."""

    ET_ALIA = "(:etal)"
    """Too numerous to list (et alia)."""


class _LinkedAgent(ComparableMixin):
    """Class holding information of a agent linked to an event."""

    def __init__(
        self,
        agent_metadata: DigitalProvenanceAgentMetadata,
        agent_role: str
    ):
        """Constructor for _LinkedAgent."""
        self.agent_metadata = agent_metadata
        self.agent_role = agent_role


class _LinkedObject(ComparableMixin):
    """Class holding information of an object linked to an event."""

    def __init__(
        self,
        object_metadata: TechnicalObjectMetadata,
        object_role: str
    ):
        """Constructor for _LinkedObject."""
        self.object_metadata = object_metadata
        self.object_role = object_role


class DigitalProvenanceEventMetadata(Metadata):
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
        detail: str,
        outcome: Union[EventOutcome, str],
        outcome_detail: str,
        datetime: Optional[str] = None,
        event_identifier_type: Optional[str] = None,
        event_identifier: Optional[str] = None,
        **kwargs
    ) -> None:
        """Constructor for DigitalProvenanceEventMetadata class.

        For advanced configurations keyword arguments for Metadata class can be
        given here as well. Look Metadata documentation for more information.

        :param event_type: A categorization of the nature of the event.
        :param detail: Additional information about the event.
        :param outcome: A categorization of the overall result of the
            event in terms of success, partial success, or failure. If given as
            string, the value is cast to EventOutcome and results in error if
            it is not a valid event outcome. The allowed values can be found
            from EventOutcome documentation.
        :param outcome_detail: A detailed description of the result or
            product of the event.
        :param datetime: The single date and time, or date and time
            range, at or during which the event occurred.

            If set to None, the event date will be generated
            during serialization and will be set to the same date on all
            metadata objects that have it set to None.

        :param event_identifier_type: Type of event identifier.
        :param event_identifier: The event identifier value. If not given by
            the user, event identifier is generated automatically.
        """
        self.event_type = event_type
        self.datetime = datetime
        self.detail = detail
        self.outcome = outcome
        self.outcome_detail = outcome_detail
        self._set_event_identifier_and_type(
            event_identifier_type, event_identifier
        )

        self.linked_agents: List[_LinkedAgent] = []
        self.linked_objects: List[_LinkedObject] = []

        super().__init__(
            metadata_type=self.METADATA_TYPE,
            metadata_format=self.METADATA_FORMAT,
            format_version=self.METADATA_FORMAT_VERSION,
            **kwargs
        )

    def _vars(self):
        vars_ = super()._vars()

        vars_["linked_agents"] = tuple(self.linked_agents)
        vars_["linked_objects"] = tuple(self.linked_objects)

        return vars_

    @property
    def outcome(self):
        """Getter for outcome."""
        return self._outcome

    @outcome.setter
    def outcome(self, outcome):
        """Setter for outcome."""
        outcome = EventOutcome(outcome)
        self._outcome = outcome

    @property
    def linked_metadata(self):
        """Return linked metadata i.e. agents and object linked to this event.

        :returns: The set of metadata linked metadata.
        """
        agents = {agent.agent_metadata for agent in self.linked_agents}
        objects = {object_.object_metadata for object_ in self.linked_objects}
        return agents | objects

    def link_agent_metadata(
        self,
        agent_metadata: DigitalProvenanceAgentMetadata,
        agent_role: str
    ) -> None:
        """Link a digital provenance agent metadata to this event.

        :param agent_metadata: The agent that is associated with this event.
        :param agent_role: The role of the agent in relation to this event.
        """
        linked_agent = _LinkedAgent(
            agent_metadata=agent_metadata,
            agent_role=agent_role
        )
        self.linked_agents.append(linked_agent)

    def link_object_metadata(
        self,
        object_metadata: TechnicalObjectMetadata,
        object_role: str
    ) -> None:
        """Link a technical object metadata to this event.

        :param object_metadata: The object metadata that is associated with
            this event.
        :param object_role: The role of the object in relation to this event.
        """
        linked_object = _LinkedObject(
            object_metadata=object_metadata,
            object_role=object_role
        )
        self.linked_objects.append(linked_object)

    def _set_event_identifier_and_type(self, identifier_type, identifier):
        """Resolve event identifier and identifier type.

        If identifier is given, also identifier type must be declared by the
        user. If identifier is not given by the user, event identifier will
        be generated later during serialization.
        """
        if identifier and not identifier_type:
            raise ValueError(
                "Event identifier type is not given, but event identifier is."
            )

        if not identifier:
            identifier_type = "UUID"
            identifier = None

        self.event_identifier_type = identifier_type
        self.event_identifier = identifier

    def _serialize_linked_agents_to_xml_elements(self, state):
        """Serialize linked agents to XML elements."""
        linked_agent_ids = [
            premis.identifier(
                identifier_type=(
                    linked_agent.agent_metadata.agent_identifier_type
                ),
                identifier_value=(
                    state.get_agent_identifier(
                        linked_agent.agent_metadata
                    )
                ),
                prefix='linkingAgent',
                role=linked_agent.agent_role
            )
            for linked_agent in self.linked_agents
        ]
        return linked_agent_ids

    def _serialize_linked_objects_to_xml_elements(self):
        """Serialize linked objects to XML elements."""
        linked_object_ids = [
            premis.identifier(
                identifier_type=(
                    linked_object.object_metadata.object_identifier_type
                ),
                identifier_value=(
                    linked_object.object_metadata.object_identifier
                ),
                prefix='linkingObject',
                role=linked_object.object_role
            )
            for linked_object in self.linked_objects
        ]
        return linked_object_ids

    def _to_xml_element_tree(self, state) -> etree._Element:
        """Serialize this metadata object to XML using lxml elements.

        :returns: The root element of the XML document
        """
        event_id_elem = premis.identifier(
            identifier_type=self.event_identifier_type,
            identifier_value=state.get_event_identifier(self),
            prefix="event"
        )

        outcome = premis.outcome(
            outcome=self.outcome.value,
            detail_note=self.outcome_detail
        )

        linked_agents = self._serialize_linked_agents_to_xml_elements(state)
        linked_objects = self._serialize_linked_objects_to_xml_elements()

        event_child_elements = [outcome] + linked_agents + linked_objects

        event = premis.event(
            event_id=event_id_elem,
            event_type=self.event_type,
            event_date_time=state.get_datetime(self),
            event_detail=self.detail,
            child_elements=event_child_elements
        )

        return event
