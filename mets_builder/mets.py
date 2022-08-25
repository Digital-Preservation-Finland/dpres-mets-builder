"""Module for METS class representing a METS document."""
from collections import namedtuple
from datetime import datetime
from datetime import timezone
from enum import Enum
import string
from typing import Optional, List, NamedTuple, Union

from mets_builder.serialize import to_xml_string

METS_CATALOG = "1.7.4"
METS_SPECIFICATION = "1.7.4"
RECORD_STATUSES = [
    "submission",
    "update",
    "dissemination"
]
METS_PROFILES = [
    "https://digitalpreservation.fi/mets-profiles/cultural-heritage",
    "https://digitalpreservation.fi/mets-profiles/research-data"
]


# TODO: In Python 3.8 this can be done more simply with
# word.isascii() and word.isprintable()
def _is_printable_us_ascii(word: str) -> bool:
    """Checks whether a string contains only printable US-ASCII
    characters.
    """
    for letter in word:
        if letter not in string.printable:
            return False
    return True


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
        mets_profile: str,
        package_id: str,
        contract_id: str,
        creator_name: str,
        creator_type: Union[AgentType, str, None] = AgentType.ORGANIZATION,
        creator_other_type: str = None,
        content_id: Optional[str] = None,
        label: Optional[str] = None,
        create_date: Optional[datetime] = None,
        last_mod_date: Optional[datetime] = None,
        record_status: Optional[str] = None,
        catalog_version: Optional[str] = METS_CATALOG,
        specification: Optional[str] = METS_SPECIFICATION
    ) -> None:
        """Constructor for METS class.

        :param str mets_profile: The METS profile for this METS document. For
            cultural heritage resources the attribute value must be
            "https://digitalpreservation.fi/mets-profiles/cultural-heritage".
            For research data resources the attribute value must be
            "https://digitalpreservation.fi/mets-profiles/research-data".
        :param str package_id: Organization’s unique identifier for the
            information package (objid). Attribute value should be expressed in
            printable US-ASCII characters.
        :param str contract_id: Contract identifier of a DPS contract to which
            the package content belongs. Attribute value should be expressed in
            printable US-ASCII characters.
        :param str creator_name: Name of the person or entity who created the
            information package.
        :param AgentType, str creator_type: Specifies the type of creator. The
            pre-defined values are:

            - INDIVIDUAL: Use if an individual has served as the creator.
            - ORGANIZATION: Use if an institution, corporate body, association,
              non-profit enterprise, government, religious body, etc. has
              served as the creator.

            Any other values should be given using the 'creator_other_type'
            attribute.
        :param str creator_other_type: Can be used to describe the creator
            type, if none of the pre-defined types in 'creator_type' attribute
            apply. If set, 'creator_other_type' overrides any value set to
            'creator_type' with AgentType.OTHER.
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
        :param str record_status: If the attribute is not present or its value
            is “submission”, the information package is a new SIP. If the
            package identifier is the same as in some other information package
            ingested earlier belonging to the same contract, the package will
            be rejected.

            The value “update” means the SIP is an updated version of a
            previous SIP. If the package identifier is not found from the DPS,
            the package will be rejected.

            The value “dissemination” means the information package is a DIP.
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
            role=AgentRole.CREATOR,
            type=creator_type,
            other_type=creator_other_type
        )

        if create_date is None:
            create_date = datetime.now(tz=timezone.utc)

        self.mets_profile = mets_profile
        self.package_id = package_id
        self.contract_id = contract_id
        self.content_id = content_id
        self.label = label
        self.create_date = create_date
        self.last_mod_date = last_mod_date
        self.record_status = record_status
        self.catalog_version = catalog_version
        self.specification = specification

    @property
    def mets_profile(self) -> str:
        """Getter for mets_profile."""
        return self._mets_profile

    @mets_profile.setter
    def mets_profile(self, value: str) -> None:
        """Setter for mets_profile."""
        if value not in METS_PROFILES:
            raise ValueError(
                f"'{value}' is not a valid value for mets_profile. "
                f"Value must be one of {METS_PROFILES}"
            )
        self._mets_profile = value

    @property
    def package_id(self) -> str:
        """Getter for package_id."""
        return self._package_id

    @package_id.setter
    def package_id(self, value: str) -> None:
        """Setter for package_id."""
        if value is None:
            raise ValueError("package_id can not be None")

        if not _is_printable_us_ascii(value):
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

        if not _is_printable_us_ascii(value):
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
        if value is not None and not _is_printable_us_ascii(value):
            raise ValueError(
                f"content_id '{value}' contains characters that are not "
                "printable US-ASCII characters"
            )
        self._content_id = value

    @property
    def record_status(self) -> Optional[str]:
        """Getter for record_status."""
        return self._record_status

    @record_status.setter
    def record_status(self, value: str) -> None:
        """Setter for record_status."""
        if value is not None and value not in RECORD_STATUSES:
            raise ValueError(
                f"'{value}' is not a valid value for record_status. "
                f"Value must be one of {RECORD_STATUSES}"
            )
        self._record_status = value

    def add_agent(
        self,
        name: str,
        *,  # This forces the rest to be given as keyword arguments
        role: Union[AgentRole, str, None] = None,
        other_role: Optional[str] = None,
        type: Union[AgentType, str, None] = None,
        other_type: Optional[str] = None
    ) -> None:
        """Add an agent to the METS object.

        Agents are a way to document different peoples' and parties' role in
        making of the information package. These agents will become agent
        elements in the metsHdr element in the final METS document.

        :param str name: The name of the agent. For example, if agent type is
            set as "ORGANIZATION", the name should be set as the name of the
            organization.
        :param AgentRole, str role: Specifies the function of the agent with
            respect to the METS record. The pre-defined values are:

            - CREATOR: The person(s) or institution(s) responsible for the METS
              document.
            - EDITOR: The person(s) or institution(s) that prepares the
              metadata for encoding.
            - ARCHIVIST: The person(s) or institution(s) responsible for the
              document/collection.
            - PRESERVATION: The person(s) or institution(s) responsible for
              preservation functions.
            - DISSEMINATOR: The person(s) or institution(s) responsible for
              dissemination functions.
            - CUSTODIAN: The person(s) or institution(s) charged with the
              oversight of a document/collection.
            - IPOWNER: Intellectual Property Owner: The person(s) or
              institution holding copyright, trade or service marks or other
              intellectual property rights for the object.

            Any other values should be given using the 'other_role' attribute.
        :param str other_role: Can be used to describe the agent role, if none
            of the pre-defined roles in 'role' attribute apply. If set,
            'other_role' overrides any value set to 'role' with
            AgentRole.OTHER.
        :param AgentType, str type: Specifies the type of agent. The
            pre-defined values are:

            - INDIVIDUAL: Use if an individual has served as the agent.
            - ORGANIZATION: Use if an institution, corporate body, association,
              non-profit enterprise, government, religious body, etc. has
              served as the agent.

            Any other values should be given using the 'other_type' attribute.
        :param str other_type: Can be used to describe the agent type, if none
            of the pre-defined types in 'type' attribute apply. If set,
            'other_type' overrides any value set to 'type' with
            AgentType.OTHER.

        :raises ValueError: if the given attributes are invalid

        :returns: None
        """
        # Handle agent role
        if other_role:
            # other_role is set, use other_role and override role
            role = AgentRole.OTHER
        elif role:
            # other_role is not set but role is, use role.

            # Cast role to AgentRole.
            # This fails if role isn't a valid agent role
            role = AgentRole(role)

            if role == AgentRole.OTHER:
                raise ValueError(
                    "Agent role is 'OTHER' but 'other_role' is not given."
                )
        else:
            raise ValueError(
                "Either 'role' or 'other_role' has to be set for the agent."
            )

        # Handle agent type
        if other_type:
            # other_type is set, use other_type and override type
            type = AgentType.OTHER
        elif type:
            # other_type is not set but type is, use type.

            # Cast type to AgentType.
            # This fails if type isn't a valid agent type
            type = AgentType(type)

            if type == AgentType.OTHER:
                raise ValueError(
                    "Agent type is 'OTHER' but 'other_type' is not given."
                )
        else:
            raise ValueError(
                "Either 'type' or 'other_type' has to be set for the agent."
            )

        METSAgent = namedtuple(
            "METSAgent", ["name", "role", "other_role", "type", "other_type"]
        )
        agent = METSAgent(name, role, other_role, type, other_type)
        self.agents.append(agent)

    def serialize(self) -> bytes:
        """Serialize this METS object into xml-formatted string."""
        return to_xml_string(self)
