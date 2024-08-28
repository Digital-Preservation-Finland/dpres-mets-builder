""""Module for TechnicalVideoMetadata class."""
from enum import Enum
from typing import Union

import videomd
from lxml import etree

from mets_builder.metadata import Metadata, MetadataFormat, MetadataType


class Color(Enum):
    """Enum for allowed color values."""
    B_AND_W = "B&W"
    COLOR = "Color"
    GRAYSCALE = "Grayscale"
    B_AND_W_WITH_GRAYSCALE_SEQUENCES = "B&W with grayscale sequences"
    B_AND_W_WITH_COLOR_SEQUENCES = "B&W with color sequences"
    GRAYSCALE_WITH_B_AND_W_SEQUENCES = "Grayscale with B&W sequences"
    GRAYSCALE_WITH_COLOR_SEQUENCES = "Grayscale with color sequences"
    COLOR_WITH_B_AND_W_SEQUENCES = "Color with B&W sequences"
    COLOR_WITH_GRAYSCALE_SEQUENCES = "Color with grayscale sequences"


class CodecQuality(Enum):
    """Enum for allowed codec quality values."""
    LOSSLESS = "lossless"
    LOSSY = "lossy"


class DataRateMode(Enum):
    """Enum for allowed data rate modes."""
    FIXED = "Fixed"
    VARIABLE = "Variable"


class Sound(Enum):
    """Enum for allowed sound values."""
    YES = "Yes"
    NO = "No"


class TechnicalVideoMetadata(Metadata):
    """Class for creating technical metadata for video files."""
    METADATA_TYPE = MetadataType.TECHNICAL
    METADATA_FORMAT = MetadataFormat.OTHER
    METADATA_OTHER_FORMAT = "VideoMD"
    METADATA_FORMAT_VERSION = "2.0"

    def __init__(
        self,
        duration: str,
        data_rate: str,
        bits_per_sample: str,
        color: Union[Color, str],
        codec_creator_app: str,
        codec_creator_app_version: str,
        codec_name: str,
        codec_quality: Union[CodecQuality, str],
        data_rate_mode: Union[DataRateMode, str],
        frame_rate: str,
        pixels_horizontal: str,
        pixels_vertical: str,
        par: str,
        dar: str,
        sampling: str,
        signal_format: str,
        sound: Union[Sound, str],
        **kwargs
    ):
        """Constructor for TechnicalVideoMetadata class.

        For advanced configurations keyword arguments for Metadata class can be
        given here as well. Look Metadata documentation for more information.

        :param duration: Elapsed time of the entire file, expressed using ISO
            8601 syntax; see http://www.w3.org/TR/NOTE-datetime.

            A value "(:unav)" can be allowed as an unknown value if the
            information cannot be easily found out.
        :param data_rate: Data rate of the audio in an MPEG or other compressed
            file expressed in mbps, e.g., "8", "12", "15", etc.

            A value "0" can be allowed as an unknown value if the information
            cannot be easily found out.
        :param bits_per_sample: The number of bits of sample depth, e.g., "8",
            "24", etc.

            A value "0" can be allowed as an unknown value if the information
            cannot be easily found out.
        :param color: Presented color of the digital video file.

            If given as string, the value is cast to Color and results in error
            if it is not a valid color. The allowed values can be found from
            Color documentation.
        :param codec_creator_app: Name of the creator of the compression
            application e.g. "Adobe Premiere"

            Values "(:unav)" or "(:unap)" can be allowed as an unknown value if
            the information cannot be easily found out. Use "(:unap)" only for
            uncompressed video.
        :param codec_creator_app_version: Version of the compression
            application e.g. "6.0"

            Values "(:unav)" or "(:unap)" can be allowed as an unknown value if
            the information cannot be easily found out. Use "(:unap)" only for
            uncompressed video or for software that does not have versioning.
        :param codec_name: Name of the compression algorithm used e.g. "MPEG"

            Values "(:unav)" or "(:unap)" can be allowed as an unknown value if
            the information cannot be easily found out. Use "(:unap)" only for
            uncompressed video.
        :param codec_quality:  Impact of the compression on quality e.g.
            "lossless" or "lossy".

            If given as string, the value is cast to CodecQuality and results
            in error if it is not a valid codec quality value. The allowed
            values can be found from CodecQuality documentation.
        :param data_rate_mode: Mode of the data rate in a digital video file.

            If given as string, the value is cast to DataRateMode and results
            in error if it is not a valid data rate mode. The allowed values
            can be found from DataRateMode documentation.
        :param frame_rate: The rate of frames displayed in one second (or
            average rate of frames per second in the case of variable
            frame-rate).  Present as a ratio of time base over frame duration,
            such as "30000/1001" or as a decimal, such as "29.970".

            A value "0" can be allowed as an unknown value if the information
            cannot be easily found out.
        :param pixels_horizontal: The horizontal dimension of a frame in
            pixels.

            A value "0" can be allowed as an unknown value if the information
            cannot be easily found out.
        :param pixels_vertical: The vertical dimension of a frame in pixels.

            A value "0" can be allowed as an unknown value if the information
            cannot be easily found out.
        :param par: Pixel aspect ratio (present as a ratio or decimal).

            A value "0" can be allowed as an unknown value if the information
            cannot be easily found out.
        :param dar: Display aspect ratio (present as a ratio or decimal such as
            "4/3" or "6/9" or "1.33333").

            Values "(:unav)" or "(:etal)" can be allowed as an unknown value if
            the information cannot be easily found out.
        :param sampling: The video sampling format used in a digital video
            file. (in terms of luminance and chrominance), e.g., "4:2:0",
            "4:2:2", "2:4:4", etc.

            Values "(:unav)" or "(:unap)" can be allowed as an unknown value if
            the information cannot be easily found out.
        :param signal_format: The signal format of a video source item e.g.
            "NTSC", "PAL", "SECAM".

            Values "(:unav)" or "(:unap)" can be allowed as an unknown value if
            the information cannot be easily found out.
        :param sound: Indicator of the presence of sound in the video file. If
            the value "Yes" is selected, then the video file should also be
            associated with an instance of audioMD (audio metadata).

            If given as string, the value is cast to Sound and results in error
            if it is not a valid sound value. The allowed values can be found
            from Sound documentation.
        """
        self.duration = duration
        self.data_rate = data_rate
        self.bits_per_sample = bits_per_sample
        self.color = color
        self.codec_creator_app = codec_creator_app
        self.codec_creator_app_version = codec_creator_app_version
        self.codec_name = codec_name
        self.codec_quality = codec_quality
        self.data_rate_mode = data_rate_mode
        self.frame_rate = frame_rate
        self.pixels_horizontal = pixels_horizontal
        self.pixels_vertical = pixels_vertical
        self.par = par
        self.dar = dar
        self.sampling = sampling
        self.signal_format = signal_format
        self.sound = sound

        super().__init__(
            metadata_type=self.METADATA_TYPE,
            metadata_format=self.METADATA_FORMAT,
            format_version=self.METADATA_FORMAT_VERSION,
            other_format=self.METADATA_OTHER_FORMAT,
            **kwargs
        )

    @property
    def color(self):
        """Getter for color."""
        return self._color

    @color.setter
    def color(self, color):
        """Setter for color."""
        color = Color(color)
        self._color = color

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
    def data_rate_mode(self):
        """Getter for data_rate_mode."""
        return self._data_rate_mode

    @data_rate_mode.setter
    def data_rate_mode(self, data_rate_mode):
        """Setter for data_rate_mode."""
        data_rate_mode = DataRateMode(data_rate_mode)
        self._data_rate_mode = data_rate_mode

    @property
    def sound(self):
        """Getter for sound."""
        return self._sound

    @sound.setter
    def sound(self, sound):
        """Setter for sound."""
        sound = Sound(sound)
        self._sound = sound

    def _to_xml_element_tree(self, state) -> etree._Element:
        """Serialize this metadata object to XML using lxml elements.

        :returns: The root element of the XML document
        """
        compression = videomd.vmd_compression(
            app=self.codec_creator_app,
            app_version=self.codec_creator_app_version,
            name=self.codec_name,
            quality=self.codec_quality.value
        )

        frame = videomd.vmd_frame(
            pixels_horizontal=self.pixels_horizontal,
            pixels_vertical=self.pixels_vertical,
            par=self.par,
            dar=self.dar
        )

        file_data = videomd.vmd_file_data(
            params={
                "duration": self.duration,
                "dataRate": self.data_rate,
                "bitsPerSample": self.bits_per_sample,
                "color": self.color.value,
                "compression": compression,
                "dataRateMode": self.data_rate_mode.value,
                "frameRate": self.frame_rate,
                "frame": frame,
                "sampling": self.sampling,
                "signalFormat": self.signal_format,
                "sound": self.sound.value
            }
        )
        return videomd.create_videomd(
            analog_digital_flag='FileDigital',
            file_data=file_data
        )
