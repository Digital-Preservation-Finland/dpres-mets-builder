"""Module for classes related to digital objects."""

import uuid
from pathlib import Path
from typing import Iterable, Optional, Union

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

        :param Iterable[MetadataBase] metadata: Iterable of metadata objects
            that describe this object.
        """
        if metadata is None:
            metadata = set()
        self.metadata = set(metadata)

    def add_metadata(self, metadata: MetadataBase) -> None:
        """Add metadata to this object.

        :param MetadataBase metadata: The metadata object that is added to this
            object.
        """
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

        :param Iterable[MetadataBase] metadata: Iterable of metadata objects
            that describe this stream.
        """
        super().__init__(metadata=metadata)


class DigitalObject(DigitalObjectBase):
    """Class representing a digital object (i.e. a file).

    DigitalObject represents a file that is included in the METS document and
    in the SIP that the METS document describes. A DigitalObject instance
    should be created for each file in the METS document, and any metadata that
    describes the file should be added to the corresponding DigitalObject
    instance.

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
        path_in_sip: Union[str, Path],
        metadata: Optional[Iterable[MetadataBase]] = None,
        streams: Optional[Iterable[DigitalObjectStream]] = None,
        identifier: Optional[str] = None
    ) -> None:
        """Constructor for DigitalObject.

        :param str, Path path_in_sip: File path of this digital object in the
            SIP, relative to the SIP root directory. Note that this can be
            different than the path in the local filesystem.
        :param Iterable[MetadataBase] metadata: Iterable of metadata objects
            that describe this stream.
        :param Iterable[DigitalObjectStream] streams: Iterable of
            DigitalObjectStreams, representing the streams of this digital
            object.
        :param str identifier: Identifier for the digital object. The
            identifier must be unique in the METS document. If None, the
            identifier is generated automatically.
        """
        super().__init__(metadata=metadata)

        self.path_in_sip = str(path_in_sip)

        if streams is None:
            streams = set()
        self.streams = set(streams)

        if identifier is None:
            # Generate identifier if identifier is not given
            identifier = "_" + str(uuid.uuid4())
        self.identifier = identifier

    def add_stream(self, stream: DigitalObjectStream) -> None:
        """Add a stream to this digital object.

        :param DigitalObjectStream stream: The stream object that is added to
            this digital object.
        """
        self.streams.add(stream)
