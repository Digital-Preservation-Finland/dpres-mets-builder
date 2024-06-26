"""Module for classes related to digital objects."""

import uuid
from pathlib import Path
from typing import Iterable, Optional, Set, Union

from mets_builder.metadata import MetadataBase


class DigitalObjectBase:
    """Base class for digital objects and streams of a digital object.

    This class is abstract and should not be instantiated.
    """

    def __init__(
        self,
        metadata: Optional[Iterable[MetadataBase]] = None
    ) -> None:
        """Constructor for DigitalObjectBase.

        :param metadata: Iterable of metadata objects that describe this
            object. Note that the metadata should be administrative metadata,
            and any descriptive metadata of a digital object should be added to
            a div in a structural map.
        """
        self.metadata: Set[MetadataBase] = set()
        if metadata is not None:
            for data in metadata:
                self.add_metadata(data)

    def add_metadata(self, metadata: MetadataBase) -> None:
        """Add administrative metadata to this object.

        Any descriptive metadata should be added to a div in structural map
        (StructuralMapDiv in a StructuralMap)

        :param metadata: The metadata object that is added to this object.

        :raises ValueError: If the given metadata is descriptive metadata.
        """
        if metadata.is_descriptive:
            raise ValueError(
                "Added metadata is descriptive metadata. Descriptive metadata "
                "should be added to a div in a structural map."
            )
        self.metadata.add(metadata)


class DigitalObjectStream(DigitalObjectBase):
    """Class representing a stream in a digital object.

    Some files may include multiple streams, for example video files may
    include separate video and audio streams. A DigitalObject instance should
    be created for the file, whereas the streams should be added to the
    DigitalObject instance as DigitalObjectStream instances using the
    DigitalObject class constructor or the `add_stream` method. Metadata
    objects describing a stream should be added to the individual stream
    objects, instead of adding them to the DigitalObject.
    """
    def __init__(
        self,
        metadata: Optional[Iterable[MetadataBase]] = None
    ) -> None:
        """Constructor for DigitalObjectStream.

        :param metadata: Iterable of metadata objects that describe this
            stream. Note that the metadata should be administrative metadata,
            and any descriptive metadata of a stream should be added to a div
            in a structural map.
        """
        super().__init__(metadata=metadata)


class DigitalObject(DigitalObjectBase):
    """Class representing a digital object (i.e. a file).

    DigitalObject represents a file that is included in the METS document and
    in the SIP that the METS document describes. A DigitalObject instance
    should be created for each file in the METS document, and any
    administrative metadata that describes the file should be added to the
    corresponding DigitalObject instance. However, any descriptive metadata
    should be added to a div in a structural map (StructuralMapDiv in a
    StructuralMap).

    Some files may include multiple streams, for example video files may
    include separate video and audio streams. A DigitalObject instance should
    be created for the file, whereas the streams should be added to the
    DigitalObject instance as DigitalObjectStream instances using the
    DigitalObject class constructor or using the `add_stream` method. Metadata
    objects describing a stream should be added to the individual stream
    objects, instead of adding them to the DigitalObject.
    """
    def __init__(
        self,
        sip_filepath: Union[str, Path],
        metadata: Optional[Iterable[MetadataBase]] = None,
        streams: Optional[Iterable[DigitalObjectStream]] = None,
        identifier: Optional[str] = None
    ) -> None:
        """Constructor for DigitalObject.

        :param sip_filepath: File path of this digital object in the SIP,
            relative to the SIP root directory. Note that this can be different
            than the path in the local filesystem.
        :param metadata: Iterable of metadata objects that describe this
            stream. Note that the metadata should be administrative metadata,
            and any descriptive metadata of a digital object should be added to
            a div in a structural map.
        :param streams: Iterable of DigitalObjectStreams, representing the
            streams of this digital object.
        :param identifier: Identifier for the digital object. The identifier
            must be unique in the METS document. If None, the identifier is
            generated automatically.
        """
        super().__init__(metadata=metadata)

        self.sip_filepath = str(sip_filepath)

        if streams is None:
            streams = set()
        self.streams = set(streams)

        if identifier is None:
            # Generate identifier if identifier is not given
            identifier = "_" + str(uuid.uuid4())
        self.identifier = identifier

    @property
    def sip_filepath(self) -> str:
        """Getter for sip_filepath."""
        return self._sip_filepath

    @sip_filepath.setter
    def sip_filepath(self, sip_filepath: Union[str, Path]) -> None:
        """Setter for sip_filepath."""
        sip_filepath = Path(sip_filepath)

        if sip_filepath.is_absolute():
            raise ValueError(
                f"Given SIP file path '{sip_filepath}' is not a relative path."
            )

        # TODO: Replace with Path.is_relative_to in Python 3.9+
        try:
            # This will raise ValueError on paths that are not relative
            sip_filepath.resolve().relative_to(Path(".").resolve())
        except ValueError:
            raise ValueError(
                f"Given SIP file path '{sip_filepath}' points outside the "
                "SIP root directory."
            )

        self._sip_filepath = str(sip_filepath)

    def add_stream(self, stream: DigitalObjectStream) -> None:
        """Add a stream to this digital object.

        :param stream: The stream object that is added to this digital object.
        """
        self.streams.add(stream)
