"""Module for ImportedMetadata class."""
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Optional, Union

import xml_helpers.utils
from lxml import etree

from mets_builder.defaults import UNAV
from mets_builder.metadata import Metadata, MetadataFormat, MetadataType
from mets_builder.metadata.mets_metadata import METS_MDTYPES


def _detect_metadata_options(xml_stream: BinaryIO) -> Optional[dict]:
    """
    Automatically detect the XML schema used in an XML document and provide
    the correct keyword arguments to be passed to `ImportedMetadata`
    """
    et_iter = etree.iterparse(xml_stream, events=("start",))

    try:
        # Only read the root element
        _, et = next(et_iter)
        schemas = set(
            et.attrib[
                "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation"
            ].split(" ")
        )
    except KeyError:
        # No schema definitions set
        schemas = set()

    # Iterate the list of recognized metadata formats and pick the one that
    # matches
    for schema_uri in schemas:
        schema_uri_ = schema_uri.strip("/")  # Strip the slash from the end

        if schema_uri_ not in METS_MDTYPES:
            continue

        options = METS_MDTYPES[schema_uri_]

        metadata_type = MetadataType.DESCRIPTIVE
        metadata_format = options.get("format", MetadataFormat.OTHER)
        format_version = options.get("version", UNAV)
        other_format = options.get("other_format", None)

        return {
            "metadata_type": metadata_type,
            "metadata_format": metadata_format,
            "format_version": format_version,
            "other_format": other_format
        }

    return None


class ImportedMetadata(Metadata):
    """Class for importing metadata files.

    .. note::

        :meth:`ImportedMetadata.from_path` or
        :meth:`ImportedMetadata.from_string` can be used to automatically
        detect the correct metadata and construct the `ImportedMetadata`
        instance
    """

    def __init__(
            self,
            metadata_type: Union[MetadataType, str],
            metadata_format: Union[MetadataFormat, str, None],
            format_version: str,
            data_path: Union[str, Path, None] = None,
            data_string: Union[str, None] = None,
            other_format: Optional[str] = None,
            created: Union[datetime, str, None] = None,
            **kwargs
    ) -> None:
        """Constructor for ImportedMetadata class.

        :param data_path: Path to the metadata file. Mutually exclusive with
            data_string.
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
        :param other_format: Can be used to define the metadata format, if
            none of the allowed values in 'metadata_format' apply. If set,
            'other_format' overrides any value given in 'metadata_format' with
            MetadataFormat.OTHER.
        :param created: The time the metadata record was created.

            If given as a datetime object, it is interpreted as the precise
            time of creation.

            If given as a string, it is interpreted as an approximate time the
            metadata record was created, and has to be given in the extended
            ISO 8601 format [ISO_8601-1, ISO_8601-2].

            If set to None, the time this object is created is used as the
            default value.
        :param data_string: String containing metadata. Mutually exclusive
            with data_path.
        """
        super().__init__(
            metadata_type=metadata_type,
            metadata_format=metadata_format,
            format_version=format_version,
            other_format=other_format,
            created=created,
            **kwargs
        )

        if data_path is None and data_string is None:
            raise ValueError("No data path or data string given")
        if data_path is not None and data_string is not None:
            raise ValueError("Both data path and data string given.")

        if data_path is not None:
            data_path = Path(data_path).resolve()
            if not data_path.is_file():
                raise ValueError(f"Given path '{data_path}' is not a file.")
            self.data_path = data_path
        else:
            self.data_string = data_string

    @classmethod
    def from_string(cls, string: bytes) -> "ImportedMetadata":
        """Create ImportedMetadata instance from an XML string.

        Metadata type, format and format version will be determined
        automatically by checking the XML schema in use.
        """
        metadata_options = _detect_metadata_options(BytesIO(string))

        if metadata_options:
            return cls(
                **metadata_options,
                data_string=string
            )

        raise ValueError(
            "Could not recognize the metadata schema of the XML document. You "
            "can try manually constructing the `ImportedMetadata` instance "
            "instead."
        )

    @classmethod
    def from_path(cls, path: Union[str, Path]) -> "ImportedMetadata":
        """Create ImportedMetadata instance from an external XML file.

        Metadata type, format and format version will be determined
        automatically by checking the XML schema in use.
        """
        with Path(path).open("rb") as file_:
            metadata_options = _detect_metadata_options(file_)

        if metadata_options:
            return cls(
                **metadata_options,
                data_path=path
            )

        raise ValueError(
            "Could not recognize the metadata schema of the XML document. You "
            "can try manually constructing the `ImportedMetadata` instance "
            "instead."
        )

    def _to_xml_element_tree(self, state) -> etree._Element:
        """Serialize this metadata object to XML using lxml elements.

        :returns: The root element of the XML document
        """
        if hasattr(self, 'data_path'):
            return xml_helpers.utils.readfile(str(self.data_path)).getroot()
        elif hasattr(self, 'data_string'):
            return etree.fromstring(self.data_string)
