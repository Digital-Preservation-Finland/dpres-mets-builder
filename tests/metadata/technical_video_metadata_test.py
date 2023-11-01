"""Tests for technical video metadata."""
from pathlib import Path

import pytest
import xml_helpers

from mets_builder.metadata import TechnicalVideoMetadata


def test_serialization():
    """Test serializing the TechnicalVideoMetadata object."""
    data = TechnicalVideoMetadata(
        duration="PT2H05M",
        data_rate="8",
        bits_per_sample="24",
        color="Color",
        codec_creator_app="SoundForge",
        codec_creator_app_version="10",
        codec_name="(:unav)",
        codec_quality="lossy",
        data_rate_mode="Fixed",
        frame_rate="24",
        pixels_horizontal="640",
        pixels_vertical="480",
        par="1.0",
        dar="4/3",
        sampling="4:2:2",
        signal_format="PAL",
        sound="No"
    )

    result = xml_helpers.utils.serialize(
        data.to_xml_element_tree()
    ).decode("utf-8")

    expected_xml = Path(
        "tests/data/expected_technical_video_metadata.xml"
    ).read_text()

    assert result == expected_xml


@pytest.mark.parametrize(
    ("invalid_init_params", "error_message"),
    (
        (
            {"color": "invalid"},
            "'invalid' is not a valid Color"
        ),
        (
            {"codec_quality": "invalid"},
            "'invalid' is not a valid CodecQuality"
        ),
        (
            {"data_rate_mode": "invalid"},
            "'invalid' is not a valid DataRateMode"
        ),
        (
            {"sound": "invalid"},
            "'invalid' is not a valid Sound"
        ),
    )
)
def test_invalid_init_parameters(invalid_init_params, error_message):
    """Test initializing TechnicalVideoMetadata with invalid parameters."""
    init_params = {
        "duration": "PT2H05M",
        "data_rate": "8",
        "bits_per_sample": "24",
        "color": "Color",
        "codec_creator_app": "SoundForge",
        "codec_creator_app_version": "10",
        "codec_name": "(:unav)",
        "codec_quality": "lossy",
        "data_rate_mode": "Fixed",
        "frame_rate": "24",
        "pixels_horizontal": "640",
        "pixels_vertical": "480",
        "par": "1.0",
        "dar": "4/3",
        "sampling": "4:2:2",
        "signal_format": "PAL",
        "sound": "No"
    }
    init_params.update(invalid_init_params)

    with pytest.raises(ValueError) as error:
        TechnicalVideoMetadata(**init_params)
    assert str(error.value) == error_message
