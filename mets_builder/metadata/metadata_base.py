"""Module for MetadataBase class and associated enums."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Union

from lxml import etree


class ChecksumAlgorithm(Enum):
    """Enum for allowed checksum algorithms."""
    MD5 = "MD5"
    SHA1 = "SHA-1"
    SHA224 = "SHA-224"
    SHA256 = "SHA-256"
    SHA384 = "SHA-384"
    SHA512 = "SHA-512"


class Charset(Enum):
    """Enum of allowed character encodings."""
    ISO8859_15 = "ISO-8859-15"
    UTF8 = "UTF-8"
    UTF16 = "UTF-16"
    UTF32 = "UTF-32"


class MetadataType(Enum):
    """Enum for metadata types."""
    TECHNICAL = "technical"
    """Technical metadata"""

    DESCRIPTIVE = "descriptive"
    """Descriptive metadata"""

    DIGITAL_PROVENANCE = "digital provenance"
    """Digital provenance metadata"""


class PREMISObjectType(Enum):
    """Enum for PREMIS object types."""
    FILE = "file"
    """Digital item representing a file"""

    BITSTREAM = "bitstream"
    """Object representing a bitstream, non stand-alone data within a file"""

    REPRESENTATION = "representation"
    """Object representing a set of file objects forming one entity"""


class MetadataFormat(Enum):
    """Enum for metadata formats."""

    # descriptive metadata formats
    MARC = "MARC"
    """MARC (Machine-Readable Cataloging), descriptive metadata format"""

    MODS = "MODS"
    """MODS (Metadata Object Description Schema), descriptive metadata
    format
    """

    DC = "DC"
    """DC (Dublin Core), descriptive metadata format"""

    EAD = "EAD"
    """EAD (Encoded Archival Description), descriptive metadata format"""

    EAC_CPF = "EAC-CPF"
    """EAD-CPF (Encoded Archival Context for Corporate Bodies, Persons, and
    Families), descriptive metadata format"""

    LIDO = "LIDO"
    """LIDO (Lightweight Information Describing Objects), descriptive metadata
    format
    """

    VRA = "VRA"
    """VRA (Visual Resources Association), descriptive metadata format"""

    DDI = "DDI"
    """DDI (Data Documentation Initiative), descriptive metadata format"""

    # technical metadata formats
    PREMIS_OBJECT = "PREMIS:OBJECT"
    """PREMIS:OBJECT, technical metadata format"""

    NISOIMG = "NISOIMG"
    """NISOIMG, technical metadata format"""

    # digital provenance metadata formats
    PREMIS_AGENT = "PREMIS:AGENT"
    """PREMIS:AGENT, digital provenance metadata format"""

    PREMIS_EVENT = "PREMIS:EVENT"
    """PREMIS:EVENT, digital provenance metadata format"""

    # other
    OTHER = "OTHER"
    """Use if none of the other options apply to the metadata format."""


class MetadataBase:
    """Base class representing metadata elements in a METS document.

    This class is abstract and should not be instantiated.
    """

    def __init__(
        self,
        metadata_type: Union[MetadataType, str],
        metadata_format: Union[MetadataFormat, str, None],
        format_version: str,
        other_format: Optional[str] = None,
        identifier: Optional[str] = None,
        created: Union[datetime, str, None] = None
    ) -> None:
        """Constructor for MetadataBase class.

        :param metadata_type: The type of metadata, given as MetadataType enum
            or string. If given as string, the value is cast to MetadataType
            and results in error if it is not a valid metadata type. The
            allowed values can be found from MetadataType enum documentation.
        :param metadata_format: The format of the metadata, given as
            MetadataFormat enum or a string. If given as string, it is cast to
            MetadataFormat and results in error if it is not a valid metadata
            format. The allowed values can be found in MetadataFormat enum
            documentation.
        :param format_version: The version number of the used metadata format,
            given as string.
        :param other_format: Can be used to define the metadata format, if none
            of the allowed values in 'metadata_format' apply. If set,
            'other_format' overrides any value given in 'metadata_format' with
            MetadataFormat.OTHER.
        :param identifier: Identifier for the metadata element. The identifier
            must be unique in the METS document. If None, the identifier is
            generated automatically.
        :param created: The time the metadata record was created.

            If given as a datetime object, it is interpreted as the precise
            time of creation.

            If given as a string, it is interpreted as an approximate time the
            metadata record was created, and has to be given in the extended
            ISO 8601 format [ISO_8601-1, ISO_8601-2].

            If set to None, the time this object is created is used as the
            default value.
        """
        # Handle metadata format and version
        if other_format:
            # other_format is set, use other_format and
            # override metadata_format
            metadata_format = MetadataFormat.OTHER
        elif metadata_format:
            # other_format is not set but metadata_format is, use
            # metadata_format.

            # Cast metadata_format to MetadataFormat. This fails if
            # metadata_format isn't a valid metadata metadata_format
            metadata_format = MetadataFormat(metadata_format)

            if metadata_format == MetadataFormat.OTHER:
                raise ValueError(
                    "'metadata_format' is 'OTHER' but 'other_format' is "
                    "not given."
                )
        else:
            raise ValueError(
                "Either 'metadata_format' or 'other_format' has to "
                "be set for the metadata."
            )
        self.metadata_format = metadata_format
        self.other_format = other_format
        self.format_version = format_version

        # Handle metadata_type
        # Cast metadata_type to MetadataType. This fails if metadata_type
        # isn't a valid metadata type
        metadata_type = MetadataType(metadata_type)
        self.metadata_type = metadata_type

        # Handle identifier
        if identifier is None:
            # Generate identifier if identifier is not given
            identifier = "_" + str(uuid.uuid4())
        self.identifier = identifier

        # Handle created
        if created is None:
            created = datetime.now(tz=timezone.utc)
        self.created = created

    @property
    def is_administrative(self) -> bool:
        """Tells if this metadata is administrative metadata.

        :returns: True if this metadata is administrative metadata, otherwise
            False.
        """
        return self.metadata_type != MetadataType.DESCRIPTIVE

    @property
    def is_descriptive(self) -> bool:
        """Tells if this metadata is descriptive metadata.

        :returns: True if this metadata is descriptive metadata, otherwise
            False.
        """
        return self.metadata_type == MetadataType.DESCRIPTIVE

    def to_xml_element_tree(self) -> etree._Element:
        """Serialize this metadata object to XML using lxml elements.

        :returns: The root element of the metadata serialized into XML.
        """
        # All metadata classes should implement this method
        raise NotImplementedError()
