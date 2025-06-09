"""Module for DigitalProvenanceObjectMetadata class."""

from lxml import etree

from mets_builder.metadata import (
    Metadata,
    MetadataFormat,
    MetadataType,
    TechnicalObjectMetadata,
)


class DigitalProvenanceObjectMetadata(Metadata):
    """Class for creating digital provenance object metadata.

    The object metadata holds representation information of the file that is
    not required to have detailed technical metadata provided.
    """

    METADATA_TYPE = MetadataType.DIGITAL_PROVENANCE
    METADATA_FORMAT = MetadataFormat.PREMIS_OBJECT
    METADATA_FORMAT_VERSION = "2.3"

    def __init__(
        self,
        object_metadata: TechnicalObjectMetadata,
        **kwargs,
    ) -> None:
        """Constructor for DigitalProvenanceObjectMetadata class.

        For advanced configurations keyword arguments for Metadata class can be
        given here as well. Look Metadata documentation for more information.

        :param name: Name of the agent.
        :param object_metadata: TechnicalObjectMetadata instance object.
        """
        self.object_metadata = object_metadata

        super().__init__(
            metadata_type=self.METADATA_TYPE,
            metadata_format=self.METADATA_FORMAT,
            format_version=self.METADATA_FORMAT_VERSION,
            **kwargs,
        )

    def _to_xml_element_tree(self, state) -> etree._Element:
        """Serialize this metadata object to an intermediate XML representation
        using lxml.

        :returns: The root element of the XML document
        """
        return self.object_metadata._to_xml_element_tree(state=state)
