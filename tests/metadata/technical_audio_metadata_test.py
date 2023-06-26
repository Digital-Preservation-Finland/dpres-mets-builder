"""Tests for technical audio metadata."""
from pathlib import Path

import pytest
import xml_helpers

from mets_builder.metadata import TechnicalAudioMetadata


def test_serialization():
    """Test serializing the TechnicalAudioMetadata object."""
    data = TechnicalAudioMetadata(
        audio_data_encoding="FLAC",
        bits_per_sample="8",
        codec_creator_app="Lavf56.40.101",
        codec_creator_app_version="56.40.101",
        codec_name="PCM",
        codec_quality="lossless",
        data_rate="706",
        data_rate_mode="Fixed",
        sampling_frequency="44.1",
        duration="PT0.86S",
        num_channels="2"
    )

    result = xml_helpers.utils.serialize(
        data.to_xml_element_tree()
    ).decode("utf-8")

    expected_xml = Path(
        "tests/data/expected_technical_audio_metadata.xml"
    ).read_text()

    assert result == expected_xml


@pytest.mark.parametrize(
    ("invalid_init_params", "error_message"),
    (
        (
            {"data_rate_mode": "invalid"},
            "'invalid' is not a valid DataRateMode"
        ),
        (
            {"codec_quality": "invalid"},
            "'invalid' is not a valid CodecQuality"
        )
    )
)
def test_invalid_init_parameters(invalid_init_params, error_message):
    """Test initializing TechnicalAudioMetadata with invalid parameters."""
    init_params = {
        "data_rate_mode": "Fixed",
        "codec_quality": "lossless"
    }
    init_params.update(invalid_init_params)

    with pytest.raises(ValueError) as error:
        TechnicalAudioMetadata(**init_params)
    assert str(error.value) == error_message


def test_data_rate_is_rounded():
    """Test that if given data rate is not an integer, it is rounded."""
    data = TechnicalAudioMetadata(
        codec_quality="lossless",
        data_rate_mode="Fixed",
        data_rate="1.1"
    )
    assert data.data_rate == "1"
