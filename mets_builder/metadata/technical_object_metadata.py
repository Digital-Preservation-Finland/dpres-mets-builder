"""Module for TechnicalObjectMetadata class."""
import uuid
from typing import Optional

import premis
from lxml import etree

from mets_builder.metadata import MetadataBase, MetadataFormat, MetadataType


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
        object_identifier_type: Optional[str] = None,
        object_identifier: Optional[str] = None,
        **kwargs
    ) -> None:
        """Constructor for TechnicalObjectMetadata class.

        For advanced configurations keyword arguments for MetadataBase class
        can be given here as well. Look MetadataBase documentation for more
        information.

        :param object_identifier_type: Type of object identifier. Standardized
            identifier types should be used when possible (e.g., an ISBN for
            books).
        :param object_identifier: The object identifier value. If not given by
            the user, object identifier is generated automatically. File
            identifiers should be globally unique.
        """
        self._set_object_identifier_and_type(
            object_identifier_type, object_identifier
        )
        super().__init__(
            metadata_type=self.METADATA_TYPE,
            metadata_format=self.METADATA_FORMAT,
            format_version=self.METADATA_FORMAT_VERSION,
            **kwargs
        )

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

    def to_xml_element_tree(self) -> etree._Element:
        """Serialize this metadata object to XML using lxml elements.

        :returns: The root element of the metadata serialized into XML.
        """
        object_id = premis.identifier(
            identifier_type=self.object_identifier_type,
            identifier_value=self.object_identifier
        )
        premis_object = premis.object(
            object_id=object_id
        )
        return premis_object
