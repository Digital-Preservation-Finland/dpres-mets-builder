"""Module for classes related to file references (METS fileSec)."""

from typing import Iterable, Optional

from mets_builder.digital_object import DigitalObject


class FileGroup:
    """Class representing fileGrp element in METS.

    Can be used to group files together in METS file references, and describing
    the purpose of the files in the group. File references must have at least
    one file group.
    """

    def __init__(
        self,
        use: Optional[str] = None,
        digital_objects: Optional[Iterable[DigitalObject]] = None
    ) -> None:
        """Constructor for FileGroup.

        :param str use: Describe the purpose of the files in this file group.
            The recommended vocabulary can be found here:
            https://digitalpreservation.fi/specifications/vocabularies
        :param Iterable[DigitalObject] digital_objects: The DigitalObjects that
            are added to the file group.
        """
        self.use = use

        if digital_objects is None:
            digital_objects = set()
        self.digital_objects = set(digital_objects)

    def add_digital_object(
        self,
        digital_object: DigitalObject
    ) -> None:
        """Add a digital object to this file group.

        :param DigitalObject digital_object: The DigitalObject that is added
            to the file group.
        """
        self.digital_objects.add(digital_object)


class FileReferences:
    """Class representing fileSec element in METS.

    The purpose of the fileSec element and this class is to link metadata to
    the digital objects they describe. This is achieved here using
    DigitalObject instances to represent individual files, adding relevant
    metadata objects to the corresponding DigitalObjects, and finally creating
    a FileReferences object out of the DigitalObjects.

    In file references digital objects can be grouped to file groups using a
    FileGroup object. A file group can have a 'use' attribute that describes
    the purpose of the files in the group, and the files are grouped together
    in METS file references under fileGrp elements. There must be at least one
    file group in the file references.

    If no special structure for file references are needed, they can be
    generated automatically using `FileReferences.generate_file_references`
    class method.
    """

    def __init__(
        self,
        file_groups: Optional[Iterable[FileGroup]] = None
    ) -> None:
        """Constructor for FileReferences.

        :param Iterable[FileGroup] file_groups: The file groups of these file
            references.
        """
        if file_groups is None:
            file_groups = set()
        self.file_groups = set(file_groups)

    def add_file_group(self, file_group: FileGroup) -> None:
        """Add a file group to these file references.

        :param FileGroup file_group: The FileGroup instance that is added to
            this FileReferences instance.
        """
        self.file_groups.add(file_group)

    @classmethod
    def generate_file_references(
        cls,
        digital_objects: Iterable[DigitalObject]
    ):
        """A shortcut method for generating simple file references.

        Returns a FileReferences instance where given digital objects have been
        grouped into a single file group.

        :param Iterable[DigitalObject] digital_objects: The DigitalObject
            instances that are included in the file references.
        """
        if not digital_objects:
            raise ValueError(
                "No digital objects given, cannot generate file references."
            )

        group = FileGroup(digital_objects=digital_objects)
        file_references = FileReferences(file_groups=[group])
        return file_references
