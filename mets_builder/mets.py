"""Module for METS class representing a METS document."""
import uuid
from collections import namedtuple
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import List, NamedTuple, Optional, Set, Union

from mets_builder import serialize, validation
from mets_builder.digital_object import DigitalObject
from mets_builder.file_references import FileReferences
from mets_builder.metadata import MetadataBase
from mets_builder.structural_map import StructuralMap

METS_CATALOG = "1.7.4"
METS_SPECIFICATION = "1.7.4"


class MetsProfile(Enum):
    """Enum for METS profiles."""

    CULTURAL_HERITAGE = (
        "https://digitalpreservation.fi/mets-profiles/cultural-heritage")
    """Profile for cultural heritage resources."""

    RESEARCH_DATA = (
        "https://digitalpreservation.fi/mets-profiles/research-data")
    """Profile for research data resources."""


class MetsRecordStatus(Enum):
    """Enum for METS record statuses."""

    SUBMISSION = "submission"
    """The information package is a new SIP. If the package identifier is the
    same as in some other information package ingested earlier belonging to the
    same contract, the package will be rejected.
    """

    UPDATE = "update"
    """The SIP is an updated version of a previous SIP."""

    DISSEMINATION = "dissemination"
    """The information package is a DIP."""


class AgentRole(Enum):
    """Enum for METS agent roles."""

    CREATOR = "CREATOR"
    """The person(s) or institution(s) responsible for the METS document."""

    EDITOR = "EDITOR"
    """The person(s) or institution(s) that prepares the metadata for
    encoding.
    """

    ARCHIVIST = "ARCHIVIST"
    """The person(s) or institution(s) responsible for the
    document/collection.
    """

    PRESERVATION = "PRESERVATION"
    """The person(s) or institution(s) responsible for preservation
    functions.
    """

    DISSEMINATOR = "DISSEMINATOR"
    """The person(s) or institution(s) responsible for dissemination
    functions.
    """

    CUSTODIAN = "CUSTODIAN"
    """The person(s) or institution(s) charged with the oversight of a
    document/collection.
    """

    IPOWNER = "IPOWNER"
    """Intellectual Property Owner: The person(s) or institution holding
    copyright, trade or service marks or other intellectual property rights for
    the object.
    """

    OTHER = "OTHER"
    """Use if none of the other options apply to the agent role."""


class AgentType(Enum):
    """Enum for METS agent types."""

    INDIVIDUAL = "INDIVIDUAL"
    """Use if an individual has served as the agent."""

    ORGANIZATION = "ORGANIZATION"
    """Use if an institution, corporate body, association, non-profit
    enterprise, government, religious body, etc. has served as the agent.
    """

    OTHER = "OTHER"
    """Use if none of the other options apply to the agent type."""


class METS:
    """Class representing a METS document."""

    def __init__(
        self,
        mets_profile: Union[MetsProfile, str],
        contract_id: str,
        creator_name: str,
        creator_type: Union[AgentType, str],
        creator_other_type: str = None,
        package_id: Optional[str] = None,
        content_id: Optional[str] = None,
        label: Optional[str] = None,
        create_date: Optional[datetime] = None,
        last_mod_date: Optional[datetime] = None,
        record_status: Union[MetsRecordStatus, str] = (
            MetsRecordStatus.SUBMISSION),
        catalog_version: Optional[str] = METS_CATALOG,
        specification: Optional[str] = METS_SPECIFICATION
    ) -> None:
        """Constructor for METS class.

        :param MetsProfile, str mets_profile: The METS profile for this
            METS document, given as MetsProfile enum or string. If given as
            string, the value is cast to MetsProfile and results in error if it
            is not a valid mets profile. The allowed values can be found from
            MetsProfile documentation.
        :param str contract_id: Contract identifier of a DPS contract to which
            the package content belongs. Attribute value should be expressed in
            printable US-ASCII characters.
        :param str creator_name: Name of the person or entity who created the
            information package.
        :param AgentType, str creator_type: The type of creator, given as
            AgentType enum or string. If given as string, the value is cast to
            AgentType and results in error if it is not a valid agent type. The
            allowed values can be found from AgentType documentation.

            If none of the AgentType values apply, any other values should be
            given using the 'creator_other_type' attribute.
        :param str creator_other_type: Can be used to describe the creator
            type, if none of the pre-defined types in 'creator_type' attribute
            apply. If set, 'creator_other_type' overrides any value set to
            'creator_type' with AgentType.OTHER.
        :param str package_id: Organization’s unique identifier for the
            information package (objid). Attribute value should be expressed in
            printable US-ASCII characters. If set to None, an UUID is generated
            as the default value.
        :param str content_id: Identifier for the content in the package.
            Attribute value should be expressed in printable US-ASCII
            characters.
        :param str label: Short description of the information package.
        :param datetime.datetime create_date: The package creation time with a
            resolution of one second. If not set, the moment when this METS
            object is created is used as default value.
        :param datetime.datetime last_mod_date: If the package has been
            modified since the initial creation, the modification time must be
            expressed with last_mod_date using the same resolution as
            create_date.
        :param MetsRecordStatus, str record_status: The record status of the
            information package, given as MetsRecordStatus enum or string. If
            given as string, the value is cast to MetsRecordStatus and results
            in error if it is not a valid record status. The allowed values can
            be found from MetsRecordStatus documentation.
        :param str catalog_version: Version number of the schema catalog used
            when data package is created. If there is no "catalog_version"
            present, it has to be replaced by "specification" attribute.
        :param str specification: Version number of packaging specification
            used in creation of data package. Mandatory only when the use of
            the "catalog_version" attribute is not possible.

        :raises ValueError: if the given attributes are invalid

        :returns: METS object
        """
        if catalog_version is None and specification is None:
            raise ValueError(
                "Either catalog_version or specification has to be set"
            )

        self.agents: List[NamedTuple] = []
        self.add_agent(
            name=creator_name,
            agent_role=AgentRole.CREATOR,
            agent_type=creator_type,
            other_type=creator_other_type
        )

        if create_date is None:
            create_date = datetime.now(tz=timezone.utc)

        if package_id is None:
            package_id = str(uuid.uuid4())

        self.mets_profile = MetsProfile(mets_profile)
        self.package_id = package_id
        self.contract_id = contract_id
        self.content_id = content_id
        self.label = label
        self.create_date = create_date
        self.last_mod_date = last_mod_date
        self.record_status = MetsRecordStatus(record_status)
        self.catalog_version = catalog_version
        self.specification = specification

        self.file_references: Optional[FileReferences] = None
        self.structural_maps: Set[StructuralMap] = set()

    @property
    def package_id(self) -> str:
        """Getter for package_id."""
        return self._package_id

    @package_id.setter
    def package_id(self, value: str) -> None:
        """Setter for package_id."""
        if value in (None, ""):
            raise ValueError("package_id cannot be empty")

        if not validation.is_printable_us_ascii(value):
            raise ValueError(
                f"package_id '{value}' contains characters that are not "
                "printable US-ASCII characters"
            )
        self._package_id = value

    @property
    def contract_id(self) -> str:
        """Getter for contract_id."""
        return self._contract_id

    @contract_id.setter
    def contract_id(self, value: str) -> None:
        """Setter for contract_id."""
        if value is None:
            raise ValueError("contract_id can not be None")

        if not validation.is_printable_us_ascii(value):
            raise ValueError(
                f"contract_id '{value}' contains characters that are not "
                "printable US-ASCII characters"
            )
        self._contract_id = value

    @property
    def content_id(self) -> Optional[str]:
        """Getter for content_id."""
        return self._content_id

    @content_id.setter
    def content_id(self, value: str) -> None:
        """Setter for content_id."""
        if value is not None and not validation.is_printable_us_ascii(value):
            raise ValueError(
                f"content_id '{value}' contains characters that are not "
                "printable US-ASCII characters"
            )
        self._content_id = value

    @property
    def metadata(self) -> Set[MetadataBase]:
        """Get all metadata that have been added to this METS via digital
        objects.
        """
        # Metadata in digital objects
        metadata: Set[MetadataBase] = set()
        for digital_object in self.digital_objects:
            metadata |= digital_object.metadata

            for stream in digital_object.streams:
                metadata |= stream.metadata

        # Metadata in structural map divs
        for structural_map in self.structural_maps:
            for div in structural_map:
                metadata |= div.metadata

        return metadata

    @property
    def digital_objects(self) -> Set[DigitalObject]:
        """Get all digital objects that have been added to this METS via a
        structural map.
        """
        digital_objects: Set[DigitalObject] = set()
        for structural_map in self.structural_maps:
            for div in structural_map:
                digital_objects |= div.digital_objects
        return digital_objects

    def add_agent(
        self,
        name: str,
        *,  # This forces the rest to be given as keyword arguments
        agent_role: Union[AgentRole, str, None] = None,
        other_role: Optional[str] = None,
        agent_type: Union[AgentType, str, None] = None,
        other_type: Optional[str] = None
    ) -> None:
        """Add an agent to the METS object.

        Agents are a way to document different peoples' and parties' role in
        making of the information package. These agents will become agent
        elements in the metsHdr element in the final METS document.

        :param str name: The name of the agent. For example, if agent type is
            set as "ORGANIZATION", the name should be set as the name of the
            organization.
        :param AgentRole, str agent_role: Specifies the function of the agent
            with respect to the METS record, given as AgentRole enum or string.
            If given as string, the value is cast to AgentRole and results in
            error if it is not a valid agent role. The allowed values can be
            found from AgentRole documentation.

            If none of the AgentRole values apply, other values should be given
            using the 'other_role' attribute.
        :param str other_role: Can be used to describe the agent role, if none
            of the pre-defined roles in 'agent_role' attribute apply. If set,
            'other_role' overrides any value set to 'agent_role' with
            AgentRole.OTHER.
        :param AgentType, str agent_type: Specifies the type of agent, given as
            AgentType enum or string. If given as string, the value is cast to
            AgentType and results in error if it is not a valid agent type. The
            allowed values can be found from AgentType documentation.

            If none of the AgentType values apply, other values should be given
            using the 'other_type' attribute.
        :param str other_type: Can be used to describe the agent type, if none
            of the pre-defined types in 'agent_type' attribute apply. If set,
            'other_type' overrides any value set to 'agent_type' with
            AgentType.OTHER.

        :raises ValueError: if the given attributes are invalid

        :returns: None
        """
        # Handle agent role
        if other_role:
            # other_role is set, use other_role and override agent_role
            agent_role = AgentRole.OTHER
        elif agent_role:
            # other_role is not set but agent_role is, use agent_role.

            # Cast agent_role to AgentRole.
            # This fails if agent_role isn't a valid agent role
            agent_role = AgentRole(agent_role)

            if agent_role == AgentRole.OTHER:
                raise ValueError(
                    "Agent role is 'OTHER' but 'other_role' is not given."
                )
        else:
            raise ValueError(
                "Either 'agent_role' or 'other_role' has to be set for the "
                "agent."
            )

        # Handle agent type
        if other_type:
            # other_type is set, use other_type and override agent_type
            agent_type = AgentType.OTHER
        elif agent_type:
            # other_type is not set but agent_type is, use agent_type.

            # Cast agent_type to AgentType.
            # This fails if agent_type isn't a valid agent type
            agent_type = AgentType(agent_type)

            if agent_type == AgentType.OTHER:
                raise ValueError(
                    "Agent type is 'OTHER' but 'other_type' is not given."
                )
        else:
            raise ValueError(
                "Either 'agent_type' or 'other_type' has to be set for the "
                "agent."
            )

        METSAgent = namedtuple(
            "METSAgent",
            ["name", "agent_role", "other_role", "agent_type", "other_type"]
        )
        agent = METSAgent(name, agent_role, other_role, agent_type, other_type)
        self.agents.append(agent)

    def add_file_references(self, file_references: FileReferences) -> None:
        """Add file references to this METS.

        This will replace any previously added file references.

        :param FileReferences file_references: FileReferences instance that is
            added to this METS.
        """
        self.file_references = file_references

    def generate_file_references(self) -> None:
        """Generate file references for this METS.

        If no special structure for file references are needed, they can be
        generated here automatically. The file references are generated out of
        the digital objects that have been added to this METS instance via
        structural maps.

        This will replace any previously added file references.
        """
        self.file_references = FileReferences.generate_file_references(
            self.digital_objects
        )

    def add_structural_map(self, structural_map: StructuralMap) -> None:
        """Add a structural map to this METS.

        :param StructuralMap structural_map: The StructuralMap instance that is
            added to this METS.
        """
        self.structural_maps.add(structural_map)

    def to_xml(self) -> bytes:
        """Serialize this METS object into XML-formatted bytestring."""
        return serialize.to_xml_string(self)

    def write(self, output_filepath: Union[str, Path]) -> None:
        """Serialize METS object to XML and write to given file path.."""
        return serialize.write_to_file(self, str(output_filepath))
