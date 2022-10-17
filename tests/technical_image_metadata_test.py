import pytest

from mets_builder.metadata import TechnicalImageMetadata
from mets_builder.serialize import _NAMESPACES


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
    md = TechnicalImageMetadata(
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

    root_element = md.serialize()

    # Root element
    assert len(root_element) == 3
    basic_do_info = root_element.find(
        "mix:BasicDigitalObjectInformation",
        namespaces=_NAMESPACES
    )
    img_info = root_element.find(
        "mix:BasicImageInformation",
        namespaces=_NAMESPACES
    )
    img_assessment = root_element.find(
        "mix:ImageAssessmentMetadata",
        namespaces=_NAMESPACES
    )
    assert basic_do_info is not None
    assert img_info is not None
    assert img_assessment is not None

    # Basic digital object information
    assert len(basic_do_info) == 2
    compression = basic_do_info.find("mix:Compression", namespaces=_NAMESPACES)
    assert compression is not None
    assert len(compression) == 1
    compression_scheme = compression.find(
        "mix:compressionScheme",
        namespaces=_NAMESPACES
    )
    assert compression_scheme is not None
    assert compression_scheme.text == "jpeg"
    byte_order = basic_do_info.find("mix:byteOrder", namespaces=_NAMESPACES)
    assert byte_order is not None
    assert byte_order.text == "little endian"

    # Basic image information
    assert len(img_info) == 1
    image_characteristics = img_info.find(
        "mix:BasicImageCharacteristics",
        namespaces=_NAMESPACES
    )
    assert image_characteristics is not None
    assert len(image_characteristics) == 3
    width = image_characteristics.find(
        "mix:imageWidth",
        namespaces=_NAMESPACES
    )
    assert width.text == "100"
    height = image_characteristics.find(
        "mix:imageHeight",
        namespaces=_NAMESPACES
    )
    assert height.text == "200"
    photometric_interpretation = image_characteristics.find(
        "mix:PhotometricInterpretation",
        namespaces=_NAMESPACES
    )
    assert photometric_interpretation is not None
    assert len(photometric_interpretation) == 2
    colorspace = photometric_interpretation.find(
        "mix:colorSpace",
        namespaces=_NAMESPACES
    )
    assert colorspace.text == "rgb"
    color_profile = photometric_interpretation.find(
        "mix:ColorProfile",
        namespaces=_NAMESPACES
    )
    assert color_profile is not None
    icc_profile = color_profile.find(
        "mix:IccProfile",
        namespaces=_NAMESPACES
    )
    assert icc_profile is not None
    icc_profile_name = icc_profile.find(
        "mix:iccProfileName",
        namespaces=_NAMESPACES
    )
    assert icc_profile_name.text == "Adobe RGB"

    # Image assessment metadata
    assert len(img_assessment) == 1
    color_encoding = img_assessment.find(
        "mix:ImageColorEncoding",
        namespaces=_NAMESPACES
    )
    assert color_encoding is not None
    assert len(color_encoding) == 2
    bits_per_sample = color_encoding.find(
        "mix:BitsPerSample",
        namespaces=_NAMESPACES
    )
    assert len(bits_per_sample) == 2
    bits_per_sample_value = bits_per_sample.find(
        "mix:bitsPerSampleValue",
        namespaces=_NAMESPACES
    )
    assert bits_per_sample_value.text == "8"
    bits_per_sample_unit = bits_per_sample.find(
        "mix:bitsPerSampleUnit",
        namespaces=_NAMESPACES
    )
    assert bits_per_sample_unit.text == "integer"
    samples_per_pixel = color_encoding.find(
        "mix:samplesPerPixel",
        namespaces=_NAMESPACES
    )
    assert samples_per_pixel.text == "3"
