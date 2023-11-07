""""Module for TechnicalCSVMetadata class."""
from typing import Iterable, List, Optional

import addml
from lxml import etree

from mets_builder.metadata import MetadataBase, MetadataFormat, MetadataType


class TechnicalCSVMetadata(MetadataBase):
    """Class for creating technical metadata for CSV files."""
    METADATA_TYPE = MetadataType.TECHNICAL
    METADATA_FORMAT = MetadataFormat.OTHER
    METADATA_OTHER_FORMAT = "ADDML"
    METADATA_FORMAT_VERSION = "8.3"

    def __init__(
        self,
        filenames: List[str],
        header: Iterable[str],
        charset: str,
        delimiter: str,
        record_separator: str,
        quoting_character: Optional[str],
        **kwargs
    ):
        """Constructor for TechnicalCSVMetadata class.

        For advanced configurations keyword arguments for MetadataBase class
        can be given here as well. Look MetadataBase documentation for more
        information.

        :param filenames: List of names of the files that the metadata
            describes. If the metadata describes only one file, the name can be
            given as string.
        :param header: Header column names of the CSV file given as an iterable
            of strings.
        :param charset: Character set used in the CSV files, e.g. "UTF-8"
        :param delimiter: The character or combination of characters that are
            used to separate fields in the CSV file.
        :param record_separator: The character or combination of characters
            that are used to separate records in the CSV file.
        :param quoting_character: The character that is used to encapsulate
            values in the CSV file. Encapsulated values can include characters
            that are otherwise treated in a special way, such as the delimiter
            character.
        """
        self.filenames = filenames
        self.header = header
        self.charset = charset
        self.delimiter = delimiter
        self.record_separator = record_separator
        self.quoting_character = quoting_character

        super().__init__(
            metadata_type=self.METADATA_TYPE,
            metadata_format=self.METADATA_FORMAT,
            format_version=self.METADATA_FORMAT_VERSION,
            other_format=self.METADATA_OTHER_FORMAT,
            **kwargs
        )

    @property
    def filenames(self) -> List[str]:
        """Getter for filenames."""
        return self._filenames

    @filenames.setter
    def filenames(self, filenames: List[str]):
        """Setter for filenames."""
        # Ensure that filenames is a list, even if a single string is given
        if isinstance(filenames, str):
            filenames = [filenames]
        self._filenames = filenames

    def to_xml_element_tree(self) -> etree._Element:
        """Serialize this metadata object to XML using lxml elements.

        :returns: The root element of the metadata serialized into XML.
        """
        # Strings used to reference sections in the serialized metadata
        flat_file_definition_reference = "ref001"
        flat_file_type_reference = "rec001"

        # Field definitions
        header_column_definitions = [
            addml.definition_elems("fieldDefinition", column, "String")
            for column in self.header
        ]
        field_definitions = addml.wrapper_elems(
            "fieldDefinitions",
            header_column_definitions
        )

        # Record definitions
        record_definition = addml.definition_elems(
            "recordDefinition",
            "record",
            child_elements=[field_definitions]
        )
        record_definitions = addml.wrapper_elems(
            "recordDefinitions",
            child_elements=[record_definition]
        )

        # Flat file definitions
        flat_file_definition = addml.definition_elems(
            "flatFileDefinition",
            flat_file_definition_reference,
            flat_file_type_reference,
            child_elements=[record_definitions]
        )
        flat_file_definitions = addml.wrapper_elems(
            "flatFileDefinitions",
            child_elements=[flat_file_definition]
        )

        # Flat file types
        charset_element = addml.addml_basic_elem("charset", self.charset)
        delim_file_format = addml.delimfileformat(
            recordseparator=self.record_separator,
            fieldseparatingchar=self.delimiter,
            quotingchar=self.quoting_character
        )
        flat_file_type = addml.definition_elems(
            "flatFileType",
            flat_file_type_reference,
            child_elements=[charset_element, delim_file_format]
        )
        flat_file_types = addml.wrapper_elems(
            "flatFileTypes",
            child_elements=[flat_file_type]
        )

        # Field types
        data_type = addml.addml_basic_elem("dataType", "string")
        field_type = addml.definition_elems(
            "fieldType",
            "String",
            child_elements=[data_type]
        )
        field_types = addml.wrapper_elems(
            "fieldTypes",
            child_elements=[field_type]
        )

        # Structure types
        structure_types = addml.wrapper_elems(
            "structureTypes",
            child_elements=[flat_file_types, field_types]
        )

        # Flat files
        flat_file_elements = [
            addml.definition_elems(
                "flatFile",
                filename,
                flat_file_definition_reference
            )
            for filename in self.filenames
        ]
        flat_files = addml.wrapper_elems(
            "flatFiles",
            child_elements=flat_file_elements + [
                flat_file_definitions, structure_types
            ]
        )

        return addml.addml(child_elements=[flat_files])
