"""Module for classes related to structural map (METS structMap)."""

from typing import Iterable, Optional, Set

from mets_builder.digital_object import DigitalObject
from mets_builder.metadata import MetadataBase
from mets_builder import validation


class StructuralMapDiv:
    """Class representing a div element in structMap in METS.

    The structural divisions of the hierarchical organization provided by a
    structural map are represented by a StructuralMapDiv division element,
    which can be nested to any depth. Each division element can represent
    either an intellectual (logical) division or a physical division.

    Any number of DigitalObjects, metadata objects or more divisions can be
    added to a StructuralMapDiv. When metadata is added to a StructMapDiv, the
    metadata applies to all DigitalObjects contained in the StructMapDiv.
    """

    def __iter__(self):
        """Iterates through all nested divs in this div. The ordering is not
        quaranteed.
        """
        for div in self.divs:
            yield div
            yield from div

    def __init__(
        self,
        div_type: str,
        order: Optional[int] = None,
        label: Optional[str] = None,
        orderlabel: Optional[str] = None,
        metadata: Optional[Iterable[MetadataBase]] = None,
        divs: Optional[Iterable["StructuralMapDiv"]] = None,
        digital_objects: Optional[Iterable[DigitalObject]] = None
    ) -> None:
        """Constructor for StructuralMapDiv.

        :param str div_type: A string that specifies the type of structural
            division that the division element represents. Possible values
            include: 'chapter', 'article', 'page', 'track', 'segment',
            'section' etc. METS places no constraints on the possible
            values. The recommended controlled vocabulary according to the
            Finnish national METS schema for the attribute can be found here:
            https://digitalpreservation.fi/specifications/vocabularies
        :param int order: A representation of the divison element's order among
            its siblings (e.g., its absolute, numeric sequence), given as
            integer value. For further of the distinction between 'order' and
            'orderlabel' see the description of the 'orderlabel' attribute.
        :param str label: A string that is used, for example, to identify a div
            to an end user viewing the document. Thus a hierarchical
            arrangement of the div label values could provide a table of
            contents to the digital content represented by a METS document and
            facilitate the users' navigation of the digital object. Note that a
            div label should be specific to its level in the structural map. In
            the case of a book with chapters, the book div label should have
            the book title and the chapter div labels should have the
            individual chapter titles, rather than having the chapter div
            labels combine both book title and chapter title. For further of
            the distinction between 'label' and 'orderlabel' see the
            description of the 'orderlabel' attribute.
        :param str orderlabel: A string representation of the element's order
            among its siblings (e.g., 'xii'), or of any non-integer native
            numbering system. It is presumed that this value will still be
            machine actionable (e.g., it would support 'go to page ___'
            function), and it should not be used as a replacement/substitute
            for the 'label' attribute. To understand the differences between
            'order', 'orderlabel' and 'label', imagine a text with 10 roman
            numbered pages followed by 10 arabic numbered pages. Page iii would
            have an 'order' of 3, an 'orderlabel' of 'iii' and a label of 'Page
            iii', while page 3 would have an 'order' of 13, an 'orderlabel' of
            '3' and a 'label' of 'Page 3'.
        :param Iterable[MetadataBase] metadata: Metadata that applies to all
            digital objects under this div.
        :param Iterable[StructuralMapDiv] divs: Divisions that this division
            should be divided further.
        :param Iterable[DigitalObject] digital_objects: Digital objects that
            belong to this hierarchical division.
        """
        self.parent: Optional["StructuralMapDiv"] = None

        self.div_type = div_type
        self.order = order
        self.label = label
        self.orderlabel = orderlabel

        self.metadata = set()
        self.digital_objects: Set[DigitalObject] = set()
        self.divs: Set["StructuralMapDiv"] = set()

        if metadata:
            self.metadata = set(metadata)

        if digital_objects:
            for digital_object in digital_objects:
                self.add_digital_object(digital_object)

        if divs:
            for div in divs:
                self.add_div(div)

    @property
    def root_div(self) -> "StructuralMapDiv":
        """Return the root div of this div. Returns self if the div has no
        parents.
        """
        parent_div = self
        while parent_div.parent is not None:
            parent_div = parent_div.parent
        return parent_div

    @property
    def nested_digital_objects(self) -> Set[DigitalObject]:
        """Get all digital objects in this div and its nested divs."""
        digital_objects = set()
        digital_objects |= self.digital_objects
        for div in self:
            digital_objects |= div.digital_objects
        return digital_objects

    def add_metadata(self, metadata: MetadataBase) -> None:
        """Add metadata to this div.

        The metadata should apply to all digital objects under this div (as
        well as digital objects under the divs nested in this div)

        :param MetadataBase metadata: The metadata object that is added to this
            div.
        """
        self.metadata.add(metadata)

    def add_div(self, div: "StructuralMapDiv") -> None:
        """Add a further division to this division.

        :param StructuralMapDiv div: The div that is added to this div.

        :raises ValueError: If the given div already exists in the div tree, if
            the added div already has a parent div, or if the added div
            contains digital objects that already exists in the div tree.
        """
        # StructuralMapDiv is iterable (the iterator iterates through all its
        # nested divs), so set(div) constructs a set of all divs in the
        # iterable (i.e. all the nested divs under the div). The div that is
        # iterated is not included in the iterator, so it has to be included
        # separately here
        added_divs = set(div) | {div}
        existing_divs = set(self.root_div) | {self.root_div}
        common_divs = added_divs & existing_divs

        if common_divs:
            raise ValueError(
                "Added div contains or is itself a div that already exists in "
                "the div tree."
            )

        if div.parent:
            raise ValueError("Added div is already has a parent div.")

        # Check for digital object conflicts
        added_objects = div.nested_digital_objects
        existing_objects = self.root_div.nested_digital_objects
        common_objects = added_objects & existing_objects
        if common_objects:
            raise ValueError(
                "Added div contains a digital object that already exists in "
                "the div tree."
            )

        div.parent = self
        self.divs.add(div)

    def add_digital_object(self, digital_object: DigitalObject) -> None:
        """Add a digital object to this div.

        :param DigitalObject digital_object: The DigitalObject that is added
            to the div.

        :raises ValueError: If the DigitalObject already exists in the div
            tree.
        """
        if digital_object in self.root_div.nested_digital_objects:
            raise ValueError(
                "Given digital object already exists in the div tree."
            )

        self.digital_objects.add(digital_object)


class StructuralMap:
    """Class representing structMap element in METS.

    The purpose of structMap element and this class is to organize the digital
    objects into a structure, and additionally to link metadata to group of
    files or the entire package, rather than just to individual digital
    objects.

    Structural map provides a means for organizing the digital objects into a
    coherent hierarchical structure. Such a hierarchical structure can be
    presented to users to facilitate their comprehension and navigation of the
    digital content. It can further be applied to any purpose requiring an
    understanding of the structural relationship of the content files or parts
    of the content files. The organization may be specified to any level of
    granularity (intellectual and or physical) that is desired. Since there can
    be multiple structural maps in a METS document, more than one organization
    can be applied to the digital content represented by the METS document. The
    hierarchical structure is achieved here by forming a tree of nested
    StructuralMapDiv objects, containing DigitalObjects.

    In addition to providing a means for organizing content, the structural map
    provides a mechanism for linking content at any hierarchical level with
    relevant metadata. This means that by linking metadata to a StructMapDiv,
    the metadata applies to all DigitalObjects that are included in the div.

    Structural map has to contain one and only one root div, that contains the
    whole structure as further nested divs, with metadata and digital objects
    linked to them.
    """

    def __iter__(self):
        """Iterate through all nested divs in this structural map. The ordering
        is not quaranteed.
        """
        yield self.root_div
        yield from self.root_div

    def __init__(
        self,
        root_div: StructuralMapDiv,
        structural_map_type: Optional[str] = None,
        label: Optional[str] = None,
        pid: Optional[str] = None,
        pid_type: Optional[str] = None
    ) -> None:
        """Constructor for StructuralMap.

        :param StrucuralMapDiv root_div: StructuralMapDiv that is the root div
            of this structural map. The structural map has to have one and only
            one root div, but the root div can contain multiple nested divs.
        :param str structural_map_type: String that identifies the type of
            structure represented by the structural map. For example, a
            structural map that represents a purely logical or intellectual
            structure could be described with value 'logical' whereas a
            structural map that represented a purely physical structure could
            be described with value 'physical'. However, the METS schema
            neither defines nor requires a common vocabulary for this
            attribute. The recommended controlled vocabulary according to the
            Finnish national METS schema for the attribute can be found here:
            https://digitalpreservation.fi/specifications/vocabularies
        :param str label: String that describes the structural map to viewers
            of the METS document. This would be useful primarily where more
            than one structural map is provided for a single object. A
            descriptive label value, in that case, could clarify to users the
            purpose of each of the available structural maps.
        :param str pid: Unique identifier of metadata, given as a string.
            Attribute value should be expressed in printable US-ASCII
            characters.
        :param str pid_type: Identifier system used in the 'pid' attribute,
            given as a string.  Attribute is mandatory if the pid attribute is
            used. Attribute value should be expressed in printable US-ASCII
            characters.
        """
        self.structural_map_type = structural_map_type
        self.label = label
        self.root_div = root_div

        # Validate that both pid and pid_type exists, or neither
        if any((pid, pid_type)) and not all((pid, pid_type)):
            raise ValueError(
                "If PID is used, both 'pid' and 'pid_type' has to be set. "
                f"Given values: 'pid': {pid}, 'pid_type': {pid_type}."
            )
        self.pid = pid
        self.pid_type = pid_type

    @property
    def pid(self) -> Optional[str]:
        """Getter for pid."""
        return self._pid

    @pid.setter
    def pid(self, value: Optional[str]) -> None:
        """Setter for pid."""
        if value is not None and not validation.is_printable_us_ascii(value):
            raise ValueError(
                f"pid '{value}' contains characters that are not "
                "printable US-ASCII characters"
            )
        self._pid = value

    @property
    def pid_type(self) -> Optional[str]:
        """Getter for pid_type."""
        return self._pid_type

    @pid_type.setter
    def pid_type(self, value: Optional[str]) -> None:
        """Setter for pid_type."""
        if value is not None and not validation.is_printable_us_ascii(value):
            raise ValueError(
                f"pid_type '{value}' contains characters that are not "
                "printable US-ASCII characters"
            )
        self._pid_type = value
