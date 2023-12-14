"""Module for TechnicalObjectMetadata class."""
import abc
import functools
import uuid
from collections import defaultdict
from typing import List, Optional, Union

import premis
from lxml import etree

from mets_builder.defaults import UNAP
from mets_builder.metadata import (Charset, ChecksumAlgorithm, MetadataBase,
                                   MetadataFormat, MetadataType,
                                   PREMISObjectType)


def _forbid_empty_value(setter):
    @functools.wraps(setter)
    def wrapper(self, value):
        if not value:
            raise ValueError(
                f"Empty value not allowed for '{setter.__name__}'"
            )

        return setter(self, value)

    return wrapper


class _Relationship():
    """Class for storing information about relationships between technical
    object metadata.
    """
    def __init__(
        self,
        object_identifier_type: str,
        object_identifier: str,
        relationship_type: str,
        relationship_subtype: str
    ):
        self.object_identifier_type = object_identifier_type
        self.object_identifier = object_identifier
        self.relationship_type = relationship_type
        self.relationship_subtype = relationship_subtype

    @property
    def type_and_subtype(self) -> tuple:
        """Get relationship type and subtype as tuple."""
        return (self.relationship_type, self.relationship_subtype)


# Technical objects take a very long list of arguments. Since
# duplicating it in many places would eventually lead to one of the copies
# becoming inconsistent with the rest, append the list of arguments dynamically
# to each docstring instead.
_OBJECT_PARAMETERS_DOC = """
        :param file_format: Mimetype of the file, e.g. 'image/tiff'.
        :param file_format_version: Version number of the file format, e.g.
            '1.2'.

            If given as '(:unap)' (unapplicable), the value will be left out
            entirely from the serialized metadata.
        :param checksum_algorithm: The specific algorithm used to construct the
            checksum for the digital object. If given as string, the value is
            cast to ChecksumAlgorithm and results in error if it is not a valid
            checksum algorithm. The allowed values can be found from
            ChecksumAlgorithm documentation.
        :param checksum: The output of the message digest algorithm.
        :param file_created_date: The actual or approximate date and time the
            object was created. The time information must be expressed using
            either the ISO-8601 format, or its extended version ISO_8601-2.
        :param object_identifier_type: Type of object identifier. Standardized
            identifier types should be used when possible (e.g., an ISBN for
            books). When set, object_identifier has to be set as well.
        :param object_identifier: The object identifier value. If not given by
            the user, object identifier is generated automatically. File
            identifiers should be globally unique. When set,
            object_identifier_type has to be set as well.
        :param charset: Character encoding of the file. If given as string, the
            value is cast to Charset and results in error if it is not a valid
            charset. The allowed values can be found from Charset
            documentation.
        :param original_name: Original name of the file.
        :param format_registry_name: Name identifying a format registry, if a
            format registry is used to give further information about the file
            format. When set, format_registry_key has to be set as well.
        :param format_registry_key: The unique key used to reference an entry
            for this file format in a format registry. When set,
            format_registry_name has to be set as well.
        :param creating_application: Software that was used to create this
            file. When set, creating_application_version has to be set as well.
        :param creating_application_version: Version of the software that was
            used to create this file. When set, creating_application has to be
            set as well.
"""


class TechnicalObjectMetadata(MetadataBase, metaclass=abc.ABCMeta):
    """Abstract class for representing technical object metadata.
    Do not instantiate this directly, use either `TechnicalFileObjectMetadata`
    or `TechnicalBitstreamObjectMetadata` instead!

    The Object entity aggregates information about a digital object held by a
    preservation repository and describes those characteristics relevant to
    preservation management.
    """
    METADATA_TYPE = MetadataType.TECHNICAL
    METADATA_FORMAT = MetadataFormat.PREMIS_OBJECT
    METADATA_FORMAT_VERSION = "2.3"

    REQUIRED_PROPERTIES = (
        "file_format",
        "file_format_version"
    )

    @abc.abstractmethod
    def __init__(
        self,
        file_format: str,
        file_format_version: str,
        checksum_algorithm: Optional[Union[ChecksumAlgorithm, str]] = None,
        checksum: Optional[str] = None,
        file_created_date: Optional[str] = None,
        object_identifier_type: Optional[str] = None,
        object_identifier: Optional[str] = None,
        charset: Union[Charset, str, None] = None,
        original_name: Optional[str] = None,
        format_registry_name: Optional[str] = None,
        format_registry_key: Optional[str] = None,
        creating_application: Optional[str] = None,
        creating_application_version: Optional[str] = None,
        **kwargs
    ) -> None:
        self.file_format = file_format
        self.file_format_version = file_format_version
        self.file_created_date = file_created_date
        self.checksum_algorithm = checksum_algorithm
        self.checksum = checksum
        self._set_object_identifier_and_type(
            object_identifier_type, object_identifier
        )
        self.charset = charset
        self.original_name = original_name
        self._set_format_registry_name_and_key(
            format_registry_name, format_registry_key
        )
        self._set_creating_application_name_and_version(
            creating_application, creating_application_version
        )

        self.relationships: List[_Relationship] = []

        super().__init__(
            metadata_type=self.METADATA_TYPE,
            metadata_format=self.METADATA_FORMAT,
            format_version=self.METADATA_FORMAT_VERSION,
            **kwargs
        )

    __init__.__doc__ = f"""Constructor for TechnicalObjectMetadata abstract
        class.

        For advanced configurations keyword arguments for MetadataBase class
        can be given here as well. Look MetadataBase documentation for more
        information.

        {_OBJECT_PARAMETERS_DOC}
        """

    def __init_subclass__(cls, **kwargs):
        """Subclass constructor for TechnicalObjectMetadata

        Make fields mandatory depending on the object type
        (eg. "file" or "bitstream") using the REQUIRED_PROPERTIES attribute
        """
        super().__init_subclass__(**kwargs)

        for field_name in cls.REQUIRED_PROPERTIES:
            orig_prop = getattr(cls, field_name)
            # Redefine the property for the subclass. The only difference
            # is the setter which is wrapped using '_forbid_empty_value'.
            setattr(
                cls, field_name,
                property(
                    fget=orig_prop.fget,
                    fset=_forbid_empty_value(orig_prop.fset),
                    fdel=orig_prop.fdel
                )
            )

    @property
    def file_format(self) -> str:
        """Getter for file_format."""
        return self._file_format

    @file_format.setter
    def file_format(self, file_format):
        """Setter for file_format."""
        self._file_format = file_format

    @property
    def file_format_version(self) -> str:
        """Getter for file_format_version."""
        return self._file_format_version

    @file_format_version.setter
    def file_format_version(self, file_format_version):
        """Setter for file_format_version."""
        self._file_format_version = file_format_version

    @property
    def checksum_algorithm(self):
        """Getter for checksum_algorithm."""
        return self._checksum_algorithm

    @checksum_algorithm.setter
    def checksum_algorithm(self, checksum_algorithm):
        """Setter for checksum_algorithm."""
        if checksum_algorithm is not None:
            checksum_algorithm = ChecksumAlgorithm(checksum_algorithm)
        self._checksum_algorithm = checksum_algorithm

    @property
    def checksum(self) -> str:
        """Getter for checksum."""
        return self._checksum

    @checksum.setter
    def checksum(self, checksum):
        """Setter for checksum."""
        self._checksum = checksum

    @property
    def charset(self):
        """Getter for charset."""
        return self._charset

    @charset.setter
    def charset(self, charset):
        """Setter for charset."""
        if charset is not None:
            charset = Charset(charset)
        self._charset = charset

    def add_relationship(
        self,
        technical_object_metadata: "TechnicalObjectMetadata",
        relationship_type: str,
        relationship_subtype: str
    ) -> None:
        """Add a relationship to another technical object metadata.

        :param technical_object_metadata: The technical object metadata object
            that is linked to this technical object metadata.
        :param relationship_type: A high-level categorization of the nature of
            the relationship.
        :param relationship_subtype: A specific characterization of the nature
            of the relationship.
        """
        relationship = _Relationship(
            object_identifier_type=(
                technical_object_metadata.object_identifier_type
            ),
            object_identifier=technical_object_metadata.object_identifier,
            relationship_type=relationship_type,
            relationship_subtype=relationship_subtype
        )

        self.relationships.append(relationship)

    def _set_object_identifier_and_type(self, identifier_type, identifier):
        """Resolve object identifier and identifier type.

        Identifier and identifier type have to either be both declared
        together, or then neither should be declared. If neither are given by
        the user, object identifier is generated as UUID.
        """
        if identifier and not identifier_type:
            raise ValueError(
                "Object identifier is given but object identifier type is not."
            )

        if identifier_type and not identifier:
            raise ValueError(
                "Object identifier type is given but object identifier is not."
            )

        if not identifier:
            identifier_type = "UUID"
            identifier = str(uuid.uuid4())

        self.object_identifier_type = identifier_type
        self.object_identifier = identifier

    def _set_format_registry_name_and_key(self, registry_name, registry_key):
        """Resolve format registry name and key.

        If one exists, the other one has to exist as well.
        """
        if registry_name and not registry_key:
            raise ValueError(
                "Format registry name is given but format registry key is not."
            )
        if not registry_name and registry_key:
            raise ValueError(
                "Format registry key is given but format registry name is not."
            )

        self.format_registry_name = registry_name
        self.format_registry_key = registry_key

    def _set_creating_application_name_and_version(
            self, creating_application, creating_application_version
    ):
        """Resolve creating application and its version.

        If one exists, the other one has to exist as well.
        """
        if creating_application and not creating_application_version:
            raise ValueError(
                "Creating application is given but creating application "
                "version is not."
            )
        if not creating_application and creating_application_version:
            raise ValueError(
                "Creating application version is given but creating "
                "application is not."
            )

        self.creating_application = creating_application
        self.creating_application_version = creating_application_version

    def _resolve_serialized_format_name(self):
        """Resolve how the file format name should be shown in the serialized
        metadata.

        If character encoding is given, it should be appended to the file
        format name.
        """
        format_name = self.file_format
        if self.charset:
            format_name += f"; encoding={self.charset.value}"
        return format_name

    def _serialize_relationships_to_xml_elements(self):
        """Serialize the relationships of this metadata to other metadata into
        XML elements.
        """
        premis_relationships = []

        # Group relationships with the same type and subtype together
        grouped_relationships = defaultdict(list)
        for relationship in self.relationships:
            group_key = relationship.type_and_subtype
            grouped_relationships[group_key].append(relationship)

        # Create a premis:relationship element for each relationship category
        for relationships in grouped_relationships.values():
            relationship_type = relationships[0].relationship_type
            relationship_subtype = relationships[0].relationship_subtype
            related_object_ids = [
                premis.identifier(
                    identifier_type=relationship.object_identifier_type,
                    identifier_value=relationship.object_identifier
                )
                for relationship in relationships
            ]

            premis_relationships.append(
                premis.relationship(
                    relationship_type=relationship_type,
                    relationship_subtype=relationship_subtype,
                    related_objects=related_object_ids
                )
            )

        return premis_relationships

    def to_xml_element_tree(self) -> etree._Element:
        """Serialize this metadata object to XML using lxml elements.

        :returns: The root element of the metadata serialized into XML.
        """
        object_id = premis.identifier(
            identifier_type=self.object_identifier_type,
            identifier_value=self.object_identifier
        )

        object_characteristics_elems = []

        # Create 'fixity' if possible
        if self.checksum:
            fixity = premis.fixity(
                message_digest=self.checksum,
                digest_algorithm=self.checksum_algorithm.value
            )
            object_characteristics_elems.append(fixity)

        # Create 'format'. This *always* exists.
        format_child_elements = []
        format_version: Optional[str] = self.file_format_version
        if format_version == UNAP:
            # If format version is given as (:unap), it should be left out of
            # the serialized metadata, as PAS interprets it as invalid value
            # for premis:formatVersion
            format_version = None
        format_designation = premis.format_designation(
            format_name=self._resolve_serialized_format_name(),
            format_version=format_version
        )
        format_child_elements.append(format_designation)
        if self.format_registry_name and self.format_registry_key:
            format_registry = premis.format_registry(
                registry_name=self.format_registry_name,
                registry_key=self.format_registry_key
            )
            format_child_elements.append(format_registry)
        format_ = premis.format(child_elements=format_child_elements)
        object_characteristics_elems.append(format_)

        # Create 'creatingApplication' if possible
        application_child_elements = []
        if self.creating_application:
            application_child_elements.append(
                premis.creating_application_name(self.creating_application)
            )
        if self.creating_application_version:
            application_child_elements.append(
                premis.creating_application_version(
                    self.creating_application_version
                )
            )
        if self.file_created_date:
            application_child_elements.append(
                premis.date_created(self.file_created_date)
            )

        if application_child_elements:
            creating_application = premis.creating_application(
                child_elements=application_child_elements
            )
            object_characteristics_elems.append(creating_application)

        object_characteristics = premis.object_characteristics(
            child_elements=object_characteristics_elems
        )
        relationships = self._serialize_relationships_to_xml_elements()
        premis_object_child_elements = [object_characteristics] + relationships

        # TODO: Make PREMIS object type in 'premis' library less awkward to
        # define. Enum should be used instead of booleans.
        is_bitstream = self.PREMIS_OBJECT_TYPE is PREMISObjectType.BITSTREAM
        is_representation = \
            self.PREMIS_OBJECT_TYPE is PREMISObjectType.REPRESENTATION

        premis_object = premis.object(
            object_id=object_id,
            original_name=self.original_name,
            child_elements=premis_object_child_elements,
            # If neither 'bitstream' or 'representation' is set, 'file' is used
            # instead.
            bitstream=is_bitstream,
            representation=is_representation
        )

        return premis_object


class TechnicalFileObjectMetadata(TechnicalObjectMetadata):
    """Class for creating technical object metadata for a single file.

    The Object entity aggregates information about a digital object held by a
    preservation repository and describes those characteristics relevant to
    preservation management.
    """
    PREMIS_OBJECT_TYPE = PREMISObjectType.FILE
    REQUIRED_PROPERTIES = (
        "file_format",
        "file_format_version",
        "checksum_algorithm",
        "checksum"
    )

    def __init__(
        self,
        file_format: str,
        file_format_version: str,
        checksum_algorithm: Union[ChecksumAlgorithm, str],
        checksum: str,
        file_created_date: str,
        object_identifier_type: Optional[str] = None,
        object_identifier: Optional[str] = None,
        charset: Union[Charset, str, None] = None,
        original_name: Optional[str] = None,
        format_registry_name: Optional[str] = None,
        format_registry_key: Optional[str] = None,
        creating_application: Optional[str] = None,
        creating_application_version: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(
            file_format=file_format,
            file_format_version=file_format_version,
            file_created_date=file_created_date,
            checksum_algorithm=checksum_algorithm,
            checksum=checksum,
            object_identifier_type=object_identifier_type,
            object_identifier=object_identifier,
            charset=charset,
            original_name=original_name,
            format_registry_name=format_registry_name,
            format_registry_key=format_registry_key,
            creating_application=creating_application,
            creating_application_version=creating_application_version,
            **kwargs)

    __init__.__doc__ = f"""Constructor for TechnicalFileObjectMetadata class.

        For advanced configurations keyword arguments for MetadataBase class
        can be given here as well. Look MetadataBase documentation for more
        information.

        {_OBJECT_PARAMETERS_DOC}
        """
