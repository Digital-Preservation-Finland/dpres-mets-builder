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


def test_invalid_data_rate_mode():
    """Test that invalid data rate modes are not allowed"""
    with pytest.raises(ValueError) as error:
        TechnicalAudioMetadata(
            audio_data_encoding="foo",
            bits_per_sample="foo",
            codec_creator_app="foo",
            codec_creator_app_version="foo",
            codec_name="foo",
            codec_quality="lossless",
            data_rate="foo",
            data_rate_mode="invalid",
            sampling_frequency="foo",
            duration="foo",
            num_channels="foo"
        )
    assert str(error.value) == "'invalid' is not a valid DataRateMode"


def test_invalid_codec_quality():
    """Test that invalid codec quality values are not allowed"""
    with pytest.raises(ValueError) as error:
        TechnicalAudioMetadata(
            audio_data_encoding="foo",
            bits_per_sample="foo",
            codec_creator_app="foo",
            codec_creator_app_version="foo",
            codec_name="foo",
            codec_quality="invalid",
            data_rate="foo",
            data_rate_mode="Fixed",
            sampling_frequency="foo",
            duration="foo",
            num_channels="foo"
        )
    assert str(error.value) == "'invalid' is not a valid CodecQuality"
