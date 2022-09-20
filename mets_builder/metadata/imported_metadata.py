"""Module for ImportedMetadata class."""

from pathlib import Path

import xml_helpers.utils
from lxml import etree

from mets_builder.metadata import MetadataBase


class ImportedMetadata(MetadataBase):
    """Class for importing metadata files."""

    def __init__(
            self,
            data_path: Path,
            **kwargs
    ) -> None:
        """Constructor for ImportedMetadata class.

        :param pathlib.Path data_path: Path to the metadata file.
        """
        super().__init__(**kwargs)

        data_path = data_path.resolve()
        if not data_path.is_file():
            raise ValueError(f"Given path '{str(data_path)}' is not a file.")
        self.data_path = data_path

    def serialize(self) -> etree._Element:
        """Serialize this metadata object to XML.

        :returns: The root element of the metadata serialized into XML.
        """
        return xml_helpers.utils.readfile(str(self.data_path)).getroot()
