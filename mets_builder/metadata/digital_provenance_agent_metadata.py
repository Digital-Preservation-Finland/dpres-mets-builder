"""Module for DigitalProvenanceAgentMetadata class."""
import uuid
from enum import Enum
from typing import Optional, Union

import premis
from lxml import etree

from mets_builder.metadata import MetadataBase, MetadataFormat, MetadataType


class DigitalProvenanceAgentType(Enum):
    """Enum for digital provenance agent types."""
    SOFTWARE = "software"
    HARDWARE = "hardware"
    PERSON = "person"
    ORGANIZATION = "organization"


class DigitalProvenanceAgentMetadata(MetadataBase):
    """Class for creating digital provenance agent metadata.

    The Agent entity aggregates information about attributes or characteristics
    of agents (persons, organizations, or software) associated with rights
    management and preservation events in the life of a data object. Agent
    information serves to identify an agent unambiguously from all other Agent
    entities.
    """
    METADATA_TYPE = MetadataType.DIGITAL_PROVENANCE
    METADATA_FORMAT = MetadataFormat.PREMIS_AGENT
    METADATA_FORMAT_VERSION = "2.3"

    def __init__(
        self,
        agent_name: str,
        agent_type: Union[DigitalProvenanceAgentType, str],
        agent_version: Optional[str] = None,
        agent_note: Optional[str] = None,
        agent_identifier_type: Optional[str] = None,
        agent_identifier: Optional[str] = None,
        **kwargs
    ) -> None:
        """Constructor for DigitalProvenanceAgentMetadata class.

        For advanced configurations keyword arguments for MetadataBase class
        can be given here as well. Look MetadataBase documentation for more
        information.

        :param agent_name: Name of the agent.
        :param agent_type: The type of this agent, given as
            DigitalProvenanceAgentType enum or string. If given as string, the
            value is cast to DigitalProvenanceAgentType and results in error if
            it is not a valid digital provenance agent type. The allowed values
            can be found from DigitalProvenanceAgentType documentation.
        :param agent_version: The version of the agent. Does not have effect if
            agent type is not 'software' or 'hardware'.
        :param agent_note: Additional information about the agent.
        :param agent_identifier_type: Type of agent identifier.
        :param agent_identifier: The agent identifier value. If not given by
            the user, agent identifier is generated automatically.
        """
        self.agent_name = agent_name
        self.agent_type = DigitalProvenanceAgentType(agent_type)
        self.agent_version = self._resolve_agent_version(
            agent_version, self.agent_type
        )
        self.agent_note = agent_note
        self._set_agent_identifier_and_type(
            agent_identifier_type, agent_identifier
        )

        super().__init__(
            metadata_type=self.METADATA_TYPE,
            metadata_format=self.METADATA_FORMAT,
            format_version=self.METADATA_FORMAT_VERSION,
            **kwargs
        )

    def _resolve_agent_version(self, agent_version, agent_type):
        """Resolve agent version.

        The version should be None unless agent type is 'software' or
        'hardware'.
        """
        if agent_type in [
            DigitalProvenanceAgentType.SOFTWARE,
            DigitalProvenanceAgentType.HARDWARE
        ]:
            return agent_version

        return None

    def _set_agent_identifier_and_type(self, identifier_type, identifier):
        """Resolve agent identifier and identifier type.

        If identifier is given, also identifier type must be declared by the
        user. If identifier is not given by the user, agent identifier should
        be generated.
        """
        if identifier and not identifier_type:
            raise ValueError(
                "Agent identifier type is not given, but agent identifier is."
            )

        if not identifier:
            identifier_type = "local"
            identifier = str(uuid.uuid4())

        self.agent_identifier_type = identifier_type
        self.agent_identifier = identifier

    def _resolve_serialized_agent_name(self):
        """Resolve how the name of the agent should be shown in the serialized
        agent.

        The name is the given agent name, unless the agent has a version
        number, in which case the version number is appended to the name.
        """
        agent_name = self.agent_name
        if self.agent_version is not None:
            agent_name = f"{agent_name}-v{self.agent_version}"
        return agent_name

    def to_xml_element_tree(self) -> etree._Element:
        """Serialize this metadata object to XML using lxml elements.

        :returns: The root element of the metadata serialized into XML.
        """
        agent_identifier = premis.identifier(
            identifier_type=self.agent_identifier_type,
            identifier_value=self.agent_identifier,
            prefix="agent",
            role=None
        )

        agent = premis.agent(
            agent_id=agent_identifier,
            agent_name=self._resolve_serialized_agent_name(),
            agent_type=self.agent_type.value,
            note=self.agent_note
        )
        return agent
