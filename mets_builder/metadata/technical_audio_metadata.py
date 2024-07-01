""""Module for TechnicalAudioMetadata class."""
from enum import Enum
from typing import Union

import audiomd
from lxml import etree

from mets_builder.metadata import Metadata, MetadataFormat, MetadataType


class CodecQuality(Enum):
    """Enum for allowed codec quality values."""
    LOSSLESS = "lossless"
    LOSSY = "lossy"


class DataRateMode(Enum):
    """Enum for allowed data rate modes."""
    FIXED = "Fixed"
    VARIABLE = "Variable"


class TechnicalAudioMetadata(Metadata):
    """Class for creating technical metadata for audio files."""

    METADATA_TYPE = MetadataType.TECHNICAL
    METADATA_FORMAT = MetadataFormat.OTHER
    METADATA_OTHER_FORMAT = "AudioMD"
    METADATA_FORMAT_VERSION = "2.0"

    def __init__(
        self,
        codec_quality: Union[CodecQuality, str],
        data_rate_mode: Union[DataRateMode, str],
        audio_data_encoding: str,
        bits_per_sample: str,
        codec_creator_app: str,
        codec_creator_app_version: str,
        codec_name: str,
        data_rate: str,
        sampling_frequency: str,
        duration: str,
        num_channels: str,
        **kwargs
    ):
        """Constructor for TechnicalAudioMetadata class.

        For advanced configurations keyword arguments for Metadata class can be
        given here as well. Look Metadata documentation for more information.

        :param codec_quality: Impact of the compression on quality e.g.
            'lossless' or 'lossy'. If given as string, the value is
            cast to CodecQuality and results in error if it is not a valid
            codec quality value. The allowed values can be found from
            CodecQuality documentation.
        :param data_rate_mode: Indicator whether the data rate is fixed or
            variable. If given as string, the value is cast to DataRateMode and
            results in error if it is not a valid data rate mode. The allowed
            values can be found from DataRateMode documentation.
        :param audio_data_encoding: Structure for audio data. If the value is
            unavailable, '(:unav)' can be used as the value.
        :param bits_per_sample: Number of bits per audio sample as a string,
            e.g. '16', '20', '24', etc. If the value is unavailable, '0' can be
            used as the value.
        :param codec_creator_app: Name of the creator of the compression
            application. If the value is unavailable, '(:unav)' can be used as
            the value. If the audio is not compressed, '(:unap)' can be used.
        :param codec_creator_app_version: Version of the compression
            application. If the value is unavailable, '(:unav)' can be used as
            the value. If the audio is not compressed or the used software
            doesn't have versioning, '(:unap)' can be used.
        :param codec_name: Name and version (or subtype) of the compression
            algorithm used, e.g. Frauenhofer 1.0. If the value is unavailable,
            '(:unav)' can be used as the value. If the audio is not compressed,
            '(:unap)' can be used.
        :param data_rate: Data rate of the audio in an MP3 or other compressed
            file, expressed in kbps, e.g., '64', '128', '256', etc. Should be
            an integer value represented as a string. Float values are rounded
            to integers automatically. If the value is unavailable, '0' can be
            used as the value.
        :param sampling_frequency: Rate at which the audio was sampled,
            expressed in kHz, e.g., '22', '44.1', '48', '96', etc. If the value
            is unavailable, '0' can be used as the value.
        :param duration: Elapsed time of the entire file, expressed using ISO
            8601 syntax. If the value is unavailable, '(:unav)' can be used as
            the value.
        :param num_channels: Number of audio channels as a string, e.g., '1',
            '2', '4', '5'. If the value is unavailable, '(:unav)' can be used
            as the value.
        """
        self.codec_quality = codec_quality
        self.data_rate_mode = data_rate_mode
        self.audio_data_encoding = audio_data_encoding
        self.bits_per_sample = bits_per_sample
        self.codec_creator_app = codec_creator_app
        self.codec_creator_app_version = codec_creator_app_version
        self.codec_name = codec_name
        self.data_rate = data_rate
        self.sampling_frequency = sampling_frequency
        self.duration = duration
        self.num_channels = num_channels

        super().__init__(
            metadata_type=self.METADATA_TYPE,
            metadata_format=self.METADATA_FORMAT,
            format_version=self.METADATA_FORMAT_VERSION,
            other_format=self.METADATA_OTHER_FORMAT,
            **kwargs
        )

    @property
    def data_rate_mode(self):
        """Getter for data_rate_mode."""
        return self._data_rate_mode

    @data_rate_mode.setter
    def data_rate_mode(self, data_rate_mode):
        """Setter for data_rate_mode."""
        data_rate_mode = DataRateMode(data_rate_mode)
        self._data_rate_mode = data_rate_mode

    @property
    def codec_quality(self):
        """Getter for codec_quality."""
        return self._codec_quality

    @codec_quality.setter
    def codec_quality(self, codec_quality):
        """Setter for codec_quality."""
        codec_quality = CodecQuality(codec_quality)
        self._codec_quality = codec_quality

    @property
    def data_rate(self):
        """Getter for data_rate."""
        return self._data_rate

    @data_rate.setter
    def data_rate(self, data_rate):
        """Setter for data_rate.

        :param data_rate: The new data_rate. The value should be an integer
            represented with a string. If given as a float, the given value is
            rounded to an integer.
        """
        rounded_data_rate = round(float(data_rate))
        self._data_rate = str(rounded_data_rate)

    def _to_xml_element_tree(self, state) -> etree._Element:
        """Serialize this metadata object to XML using lxml elements.

        :returns: The root element of the metadata serialized into XML.
        """
        compression = audiomd.amd_compression(
            app=self.codec_creator_app,
            app_version=self.codec_creator_app_version,
            name=self.codec_name,
            quality=self.codec_quality.value
        )

        file_data_params = {
            "audioDataEncoding": self.audio_data_encoding,
            "bitsPerSample": self.bits_per_sample,
            "compression": compression,
            "dataRate": self.data_rate,
            "dataRateMode": self.data_rate_mode.value,
            "samplingFrequency": self.sampling_frequency
        }
        file_data = audiomd.amd_file_data(file_data_params)

        audio_info = audiomd.amd_audio_info(
            duration=self.duration,
            num_channels=self.num_channels
        )

        return audiomd.create_audiomd(
            file_data=file_data,
            audio_info=audio_info
        )
