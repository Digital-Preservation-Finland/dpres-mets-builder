from pathlib import Path
import pytest

from lxml import etree

from mets_builder.metadata import TechnicalImageMetadata


@pytest.mark.parametrize(
    ["invalid_modifications"],
    [
        # Missing compression
        [{"compression": None}],
        [{"compression": "(:unav)"}],
        # Missing colorspace
        [{"colorspace": None}],
        [{"colorspace": "(:unav)"}],
        # Missing width
        [{"width": None}],
        [{"width": "(:unav)"}],
        # Missing height
        [{"height": None}],
        [{"height": "(:unav)"}],
        # Missing bps_value
        [{"bps_value": None}],
        [{"bps_value": "(:unav)"}],
        # Missing bps_unit
        [{"bps_unit": None}],
        [{"bps_unit": "(:unav)"}],
        # Missing samples_per_pixel
        [{"samples_per_pixel": None}],
        [{"samples_per_pixel": "(:unav)"}],
        # TIFF image missing byte_order
        [{"mimetype": "image/tiff", "byte_order": None}],
        [{"mimetype": "image/tiff", "byte_order": "(:unav)"}]
    ]
)
def test_invalid_parameters(invalid_modifications):
    """Test that invalid init parameters raise ValueError"""
    init_parameters = {
        "compression": "jpeg",
        "colorspace": "rbg",
        "width": "100",
        "height": "100",
        "bps_value": "8",
        "bps_unit": "integer",
        "samples_per_pixel": "3"
    }

    for key, value in invalid_modifications.items():
        init_parameters[key] = value

    with pytest.raises(ValueError):
        TechnicalImageMetadata(**init_parameters)


def test_serialization():
    """Test serializing the TechnicalImageMetadata object."""
    data = TechnicalImageMetadata(
        compression="jpeg",
        colorspace="rgb",
        width="100",
        height="200",
        bps_value="8",
        bps_unit="integer",
        samples_per_pixel="3",
        mimetype="image/jpeg",
        byte_order="little endian",
        icc_profile_name="Adobe RGB"
    )

    result = etree.tostring(
        data.to_xml_element_tree(),
        pretty_print=True,
        encoding="UTF-8"
    ).decode("utf-8")

    expected_xml = Path(
        "tests/data/expected_technical_image_metadata.xml"
    ).read_text()

    assert result == expected_xml
