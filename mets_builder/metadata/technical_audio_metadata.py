""""Module for TechnicalAudioMetadata class."""
import audiomd
from lxml import etree

from mets_builder.metadata import MetadataBase, MetadataFormat, MetadataType


class TechnicalAudioMetadata(MetadataBase):
    """Class for creating technical metadata for audio files."""

    METADATA_TYPE = MetadataType.TECHNICAL
    METADATA_FORMAT = MetadataFormat.OTHER
    METADATA_OTHER_FORMAT = "AudioMD"
    METADATA_FORMAT_VERSION = "2.0"

    def __init__(
        self,
        audio_data_encoding: str,
        bits_per_sample: str,
        codec_creator_app: str,
        codec_creator_app_version: str,
        codec_name: str,
        codec_quality: str,
        data_rate: str,
        data_rate_mode: str,
        sampling_frequency: str,
        duration: str,
        num_channels: str,
        **kwargs
    ):
        """Constructor for TechnicalAudioMetadata class.

        For advanced configurations keyword arguments for MetadataBase class
        can be given here as well. Look MetadataBase documentation for more
        information.

        :param audio_data_encoding: Structure for audio data.
        :param bits_per_sample: Number of bits per audio sample as a string,
            e.g. '16', '20', '24', etc.
        :param codec_creator_app: Name of the creator of the compression
            application.
        :param codec_creator_app_version: Version of the compression
            application
        :param codec_name: Name and version (or subtype) of the compression
            algorithm used, e.g. Frauenhofer 1.0
        :param codec_quality: Impact of the compression on quality e.g.
            'lossless' or 'lossy'.
        :param data_rate: Data rate of the audio in an MP3 or other compressed
            file, expressed in kbps, e.g., '64', '128', '256', etc.
        :param data_rate_mode: Indicator whether the data rate is fixed or
            variable.
        :param sampling_frequency: Rate at which the audio was sampled,
            expressed in kHz, e.g., '22', '44.1', '48', '96', etc.
        :param duration: Elapsed time of the entire file, expressed using ISO
            8601 syntax.
        :param num_channels: Number of audio channels as a string, e.g., '1',
            '2', '4', '5'.
        """
        self.audio_data_encoding = audio_data_encoding
        self.bits_per_sample = bits_per_sample
        self.codec_creator_app = codec_creator_app
        self.codec_creator_app_version = codec_creator_app_version
        self.codec_name = codec_name
        self.codec_quality = codec_quality
        self.data_rate = data_rate
        self.data_rate_mode = data_rate_mode
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

    def to_xml_element_tree(self) -> etree._Element:
        """Serialize this metadata object to XML using lxml elements.

        :returns: The root element of the metadata serialized into XML.
        """
        compression = audiomd.amd_compression(
            app=self.codec_creator_app,
            app_version=self.codec_creator_app_version,
            name=self.codec_name,
            quality=self.codec_quality
        )

        file_data_params = {
            "audioDataEncoding": self.audio_data_encoding,
            "bitsPerSample": self.bits_per_sample,
            "compression": compression,
            "dataRate": self.data_rate,
            "dataRateMode": self.data_rate_mode,
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
