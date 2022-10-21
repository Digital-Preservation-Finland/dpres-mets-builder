""""Module for TechnicalImageMetadata class."""

from typing import Optional

import nisomix
from lxml import etree

from mets_builder.defaults import UNAV
from mets_builder.metadata import MetadataBase, MetadataFormat, MetadataType


class TechnicalImageMetadata(MetadataBase):
    """Class for creating technical metadata for image files."""

    METADATA_TYPE = MetadataType.TECHNICAL
    METADATA_FORMAT = MetadataFormat.NISOIMG
    METADATA_FORMAT_VERSION = "2.0"

    def __init__(
        self,
        compression: str,
        colorspace: str,
        width: str,
        height: str,
        bps_value: str,
        bps_unit: str,
        samples_per_pixel: str,
        mimetype: Optional[str] = None,
        byte_order: Optional[str] = None,
        icc_profile_name: Optional[str] = None,
        **kwargs
    ) -> None:
        """Constructor for TechnicalImageMetadata class.

        For advanced configurations keyword arguments for MetadataBase class
        can be given here as well. Look MetadataBase documentation for more
        information.

        :param str compression: Compression scheme, e.g. 'jpeg' or 'zip'
        :param str colorspace: Color space of the image, e.g. 'rgb'
        :param str width: Width of the image as pixels.
        :param str height: Height of the image as pixels.
        :param str bps_value: Bits per sample.
        :param str bps_unit: Unit of the bps_value, e.g. 'integer'
        :param str samples_per_pixel: Samples per pixel.
        :param str mimetype: File mimetype, e.g. 'image/tiff'.
        :param str byte_order: Byte order of the file, e.g. 'little endian'
        :param str icc_profile_name: ICC profile name.
        """
        self.compression = compression
        self.colorspace = colorspace
        self.width = width
        self.height = height
        self.bps_value = bps_value
        self.bps_unit = bps_unit
        self.samples_per_pixel = samples_per_pixel
        self.mimetype = mimetype
        self.byte_order = byte_order
        self.icc_profile_name = icc_profile_name

        # Check that values that have to be present are present
        self._check_missing_metadata()

        if mimetype == "image/tiff" and byte_order in (None, UNAV):
            raise ValueError(
                "Byte order missing from TIFF image metadata."
            )

        super().__init__(
            metadata_type=self.METADATA_TYPE,
            metadata_format=self.METADATA_FORMAT,
            format_version=self.METADATA_FORMAT_VERSION,
            **kwargs
        )

    def _check_missing_metadata(self):
        """Check that metadata that is supposed to be present is present.
        Otherwise raise an error.
        """
        has_to_be_present = {
            "compression": self.compression,
            "colorspace": self.colorspace,
            "width": self.width,
            "height": self.height,
            "bps_value": self.bps_value,
            "bps_unit": self.bps_unit,
            "samples_per_pixel": self.samples_per_pixel
        }
        for key, value in has_to_be_present.items():
            if value in (None, UNAV):
                raise ValueError(
                    f"Missing metadata value for key '{key}'. Given value was "
                    f"{value}."
                )

    def to_xml_element_tree(self) -> etree._Element:
        """Serialize this metadata object to XML using lxml elements.

        :returns: The root element of the metadata serialized into XML.
        """
        # Basic digital object information
        mix_compression = nisomix.compression(
            compression_scheme=self.compression)
        basic_do_info = nisomix.digital_object_information(
            byte_order=self.byte_order,
            child_elements=[mix_compression]
        )

        # Basic image information
        if self.icc_profile_name not in (UNAV, None):
            color_profile = [
                nisomix.color_profile(
                    icc_name=self.icc_profile_name
                )
            ]
        else:
            color_profile = None
        photom_interpret = nisomix.photometric_interpretation(
            color_space=self.colorspace,
            child_elements=color_profile
        )
        img_characteristics = nisomix.image_characteristics(
            width=self.width,
            height=self.height,
            child_elements=[photom_interpret]
        )
        img_info = nisomix.image_information(
            child_elements=[img_characteristics]
        )

        # Image assessment metadata
        bit_depth = nisomix.bits_per_sample(
            sample_values=self.bps_value,
            sample_unit=self.bps_unit
        )
        color_encoding = nisomix.color_encoding(
            samples_pixel=self.samples_per_pixel,
            child_elements=[bit_depth]
        )
        img_assessment = nisomix.image_assessment_metadata(
            child_elements=[color_encoding]
        )

        # Root element
        mix_root = nisomix.mix(
            child_elements=[basic_do_info, img_info, img_assessment]
        )

        return mix_root
