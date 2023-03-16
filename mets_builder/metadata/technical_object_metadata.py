"""Module for TechnicalObjectMetadata class."""
import uuid
from typing import Optional, Union

import premis
from lxml import etree

from mets_builder.metadata import (Charset, ChecksumAlgorithm, MetadataBase,
                                   MetadataFormat, MetadataType)


class TechnicalObjectMetadata(MetadataBase):
    """Class for creating technical object metadata.

    The Object entity aggregates information about a digital object held by a
    preservation repository and describes those characteristics relevant to
    preservation management.
    """
    METADATA_TYPE = MetadataType.TECHNICAL
    METADATA_FORMAT = MetadataFormat.PREMIS_OBJECT
    METADATA_FORMAT_VERSION = "2.3"

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
        **kwargs
    ) -> None:
        """Constructor for TechnicalObjectMetadata class.

        For advanced configurations keyword arguments for MetadataBase class
        can be given here as well. Look MetadataBase documentation for more
        information.

        :param file_format: Mimetype of the file, e.g. 'image/tiff'
        :param file_format_version: Version number of the file format, e.g.
            '1.2'.
        :param file_created_date: The actual or approximate date and time the
            object was created. The time information must be expressed using
            either the ISO-8601 format, or its extended version ISO_8601-2.
        :param checksum_algorithm: The specific algorithm used to construct the
            checksum for the digital object. If given as string, the value is
            cast to ChecksumAlgorithm and results in error if it is not a valid
            checksum algorithm. The allowed values can be found from
            ChecksumAlgorithm documentation.
        :param checksum: The output of the message digest algorithm.
        :param object_identifier_type: Type of object identifier. Standardized
            identifier types should be used when possible (e.g., an ISBN for
            books).
        :param object_identifier: The object identifier value. If not given by
            the user, object identifier is generated automatically. File
            identifiers should be globally unique.
        :param charset: Character encoding of the file. If given as string, the
            value is cast to Charset and results in error if it is not a valid
            charset. The allowed values can be found from Charset
            documentation.
        :param original_name: Original name of the file.
        :param format_registry_name: Name identifying a format registry, if a
            format registry is used to give further information about the file
            format.
        :param format_registry_key: The unique key used to reference an entry
            for this file format in a format registry.
        """
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

        super().__init__(
            metadata_type=self.METADATA_TYPE,
            metadata_format=self.METADATA_FORMAT,
            format_version=self.METADATA_FORMAT_VERSION,
            **kwargs
        )

    @property
    def checksum_algorithm(self):
        """Getter for checksum_algorithm."""
        return self._checksum_algorithm

    @checksum_algorithm.setter
    def checksum_algorithm(self, checksum_algorithm):
        """Setter for checksum_algorithm."""
        checksum_algorithm = ChecksumAlgorithm(checksum_algorithm)
        self._checksum_algorithm = checksum_algorithm

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

    def _set_object_identifier_and_type(self, identifier_type, identifier):
        """Resolve object identifier and identifier type.

        If identifier is given, also identifier type must be declared by the
        user. If identifier is not given by the user, object identifier should
        be generated.
        """
        if identifier and not identifier_type:
            raise ValueError(
                "Object identifier type is not given, but object identifier "
                "is."
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
                "Format registry name is given, but not format registry key."
            )
        if not registry_name and registry_key:
            raise ValueError(
                "Format registry key is given, but not format registry name."
            )

        self.format_registry_name = registry_name
        self.format_registry_key = registry_key

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

    def to_xml_element_tree(self) -> etree._Element:
        """Serialize this metadata object to XML using lxml elements.

        :returns: The root element of the metadata serialized into XML.
        """
        object_id = premis.identifier(
            identifier_type=self.object_identifier_type,
            identifier_value=self.object_identifier
        )

        fixity = premis.fixity(
            message_digest=self.checksum,
            digest_algorithm=self.checksum_algorithm.value
        )

        format_child_elements = []
        format_designation = premis.format_designation(
            format_name=self._resolve_serialized_format_name(),
            format_version=self.file_format_version
        )
        format_child_elements.append(format_designation)
        if self.format_registry_name and self.format_registry_key:
            format_registry = premis.format_registry(
                registry_name=self.format_registry_name,
                registry_key=self.format_registry_key
            )
            format_child_elements.append(format_registry)
        format_ = premis.format(child_elements=format_child_elements)

        application_created_date = premis.date_created(self.file_created_date)
        creating_application = premis.creating_application(
            child_elements=[application_created_date]
        )

        object_characteristics = premis.object_characteristics(
            child_elements=[fixity, format_, creating_application]
        )

        premis_object = premis.object(
            object_id=object_id,
            original_name=self.original_name,
            child_elements=[object_characteristics]
        )

        return premis_object
