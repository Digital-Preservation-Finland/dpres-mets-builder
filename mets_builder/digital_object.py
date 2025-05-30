"""Module for classes related to digital objects."""

from pathlib import Path
from typing import Iterable, Optional, Set, Union

from mets_builder.metadata import Metadata, MetadataFormat
from mets_builder.uuid import underscore_uuid


class DigitalObjectBase:
    """Base class for digital objects and streams of a digital object.

    This class is abstract and should not be instantiated.
    """

    def __init__(
        self,
        metadata: Optional[Iterable[Metadata]] = None
    ) -> None:
        """Constructor for DigitalObjectBase.

        :param metadata: Iterable of metadata objects that describe this
            object. Note that the metadata should be administrative metadata,
            and any descriptive metadata of a digital object should be added to
            a div in a structural map.
        """
        self.metadata: Set[Metadata] = set()
        if metadata is not None:
            self.add_metadata(metadata)

    def add_metadata(self, metadata: Iterable[Metadata]) -> None:
        """Add administrative metadata to this object.

        Any descriptive metadata should be added to a div in structural map
        (StructuralMapDiv in a StructuralMap)

        :param metadata: The iterable containing metadata objects that are
            added to this object.

        :raises ValueError: If the given metadata is descriptive metadata.
        """
        for metadata_element in metadata:
            if metadata_element.is_descriptive:
                raise ValueError(
                    "Added metadata is descriptive metadata. Descriptive "
                    "metadata should be added to a div in a structural map."
                )
        self.metadata |= set(metadata)

        # Automatically add any linked agents as well
        for metadata_element in metadata:
            self.metadata |= {
                linked_metadata for linked_metadata
                in metadata_element.linked_metadata
                if linked_metadata.METADATA_FORMAT
                == MetadataFormat.PREMIS_AGENT
            }


class DigitalObjectStream(DigitalObjectBase):
    """Class representing a stream in a digital object.

    Some files may include multiple streams, for example video files may
    include separate video and audio streams. A DigitalObject instance should
    be created for the file, whereas the streams should be added to the
    DigitalObject instance as DigitalObjectStream instances using the
    DigitalObject class constructor or the :meth:`DigitalObject.add_streams`
    method. Metadata objects describing a stream should be added to the
    individual stream objects, instead of adding them to the DigitalObject.
    """
    def __init__(
        self,
        metadata: Optional[Iterable[Metadata]] = None
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
    DigitalObject class constructor or using the
    :meth:`DigitalObject.add_streams` method. Metadata objects describing a
    stream should be added to the individual stream objects, instead of adding
    them to the DigitalObject.
    """
    def __init__(
        self,
        path: Union[str, Path],
        metadata: Optional[Iterable[Metadata]] = None,
        streams: Optional[Iterable[DigitalObjectStream]] = None,
        identifier: Optional[str] = None,
        use: Optional[str] = None
    ) -> None:
        """Constructor for DigitalObject.

        :param path: File path of this digital object in the SIP,
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
        :param use: USE attribute of file. USE attribute defines usage
            of file. The recommended controlled vocabulary for
            attribute:
            https://digitalpreservation.fi/resources/vocabulary
        """
        super().__init__(metadata=metadata)

        self.path = str(path)

        if streams is None:
            streams = set()
        self.streams = set(streams)

        if identifier is None:
            identifier = underscore_uuid()
        self.identifier = identifier

        self.use = use

    @property
    def path(self) -> str:
        """Getter for path."""
        return self._path

    @path.setter
    def path(self, path: Union[str, Path]) -> None:
        """Setter for path."""
        path = Path(path)

        if path.is_absolute():
            raise ValueError(
                f"Given SIP file path '{path}' is not a relative path."
            )

        if not path.resolve().is_relative_to(Path(".").resolve()):
            raise ValueError(
                f"Given SIP file path '{path}' points outside the "
                "SIP root directory."
            )

        self._path = str(path)

    def add_streams(self, streams: Iterable[DigitalObjectStream]) -> None:
        """Add streams to this digital object.

        :param stream: The iterable containing stream objects that are added to
            this digital object.
        """
        self.streams |= set(streams)
