"""Tests for technical audio metadata."""
from pathlib import Path

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
        data_rate="705.6",
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
