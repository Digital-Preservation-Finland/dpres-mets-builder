"""Module for classes related to structural map (METS structMap)."""
from typing import Iterable, Optional, Set

from mets_builder.digital_object import DigitalObject
from mets_builder.metadata import Metadata, MetadataType


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
        metadata: Optional[Iterable[Metadata]] = None,
        divs: Optional[Iterable["StructuralMapDiv"]] = None,
        digital_objects: Optional[Iterable[DigitalObject]] = None
    ) -> None:
        """Constructor for StructuralMapDiv.

        :param div_type: A string that specifies the type of structural
            division that the division element represents. Possible values
            include: 'chapter', 'article', 'page', 'track', 'segment',
            'section' etc. METS places no constraints on the possible values.
        :param order: A representation of the divison element's order among its
            siblings (e.g., its absolute, numeric sequence), given as integer
            value. For further of the distinction between 'order' and
            'orderlabel' see the description of the 'orderlabel' attribute.
        :param label: A string that is used, for example, to identify a div to
            an end user viewing the document. Thus a hierarchical arrangement
            of the div label values could provide a table of contents to the
            digital content represented by a METS document and facilitate the
            users' navigation of the digital object. Note that a div label
            should be specific to its level in the structural map. In the case
            of a book with chapters, the book div label should have the book
            title and the chapter div labels should have the individual chapter
            titles, rather than having the chapter div labels combine both book
            title and chapter title. For further of the distinction between
            'label' and 'orderlabel' see the description of the 'orderlabel'
            attribute.
        :param orderlabel: A string representation of the element's order among
            its siblings (e.g., 'xii'), or of any non-integer native numbering
            system. It is presumed that this value will still be machine
            actionable (e.g., it would support 'go to page ___' function), and
            it should not be used as a replacement/substitute for the 'label'
            attribute. To understand the differences between 'order',
            'orderlabel' and 'label', imagine a text with 10 roman numbered
            pages followed by 10 arabic numbered pages. Page iii would have an
            'order' of 3, an 'orderlabel' of 'iii' and a label of 'Page iii',
            while page 3 would have an 'order' of 13, an 'orderlabel' of '3'
            and a 'label' of 'Page 3'.
        :param metadata: Metadata that applies to all digital objects under
            this div.
        :param divs: Divisions that this division should be divided further.
        :param digital_objects: Digital objects that belong to this
            hierarchical division.
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
            self.add_metadata(metadata)

        if digital_objects:
            self.add_digital_objects(digital_objects)

        if divs:
            self.add_divs(divs)

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

    def add_metadata(self, metadata: Iterable[Metadata]) -> None:
        """Add metadata to this div.

        The metadata should apply to all digital objects under this div (as
        well as digital objects under the divs nested in this div)

        :param metadata: The iterable containing metadata objects that are
            added to this div.
        """
        self.metadata |= set(metadata)
        for metadata_element in metadata:
            self.metadata |= set(metadata_element.linked_metadata)

    def add_divs(self, divs: Iterable["StructuralMapDiv"]) -> None:
        """Add a further divisions to this division.

        Note that it is much more performant add multiple divs at once, rather
        than adding divs one by one.

        :param divs: An iterable of StructuralMapDivs that are added to this
            div.

        :raises ValueError: If the given div already exists or contains a div
            that exists in the div tree, if the added div already has a parent
            div, or if any of the added divs contain digital objects that
            already exists in the div tree.
        """
        # Check that divs is not a sungle StructuralMapDiv, because as
        # StructuralMapDiv is an iterable the following code would run but with
        # unwanted results.
        if isinstance(divs, StructuralMapDiv):
            raise TypeError(
                "Given 'divs' is a single StructuralMapDiv. Give an iterable "
                "of StructuralMapDivs as the 'divs' argument."
            )

        # StructuralMapDiv is iterable (the iterator iterates through all its
        # nested divs), so set(div) constructs a set of all divs in the
        # iterable (i.e. all the nested divs under the div). The div that is
        # iterated is not included in the iterator, so it has to be included
        # separately here
        added_divs = set()
        for div in divs:
            added_divs = set(div) | {div}
        existing_divs = set(self.root_div) | {self.root_div}
        common_divs_exist = not added_divs.isdisjoint(existing_divs)

        if common_divs_exist:
            raise ValueError(
                "Added div contains or is itself a div that already exists in "
                "the div tree."
            )

        for div in divs:
            if div.parent:
                raise ValueError("An added div is already has a parent div.")

        # Check for digital object conflicts
        added_objects = set()
        for div in divs:
            added_objects |= div.nested_digital_objects
        existing_objects = self.root_div.nested_digital_objects
        common_objects_exist = not added_objects.isdisjoint(existing_objects)
        if common_objects_exist:
            raise ValueError(
                "An added div contains a digital object that already exists "
                "in the div tree."
            )

        # Set this div as the parent for all added divs
        for div in divs:
            div.parent = self

        # Add the divs to this div
        self.divs |= set(divs)

    def add_digital_objects(
        self,
        digital_objects: Iterable[DigitalObject]
    ) -> None:
        """Add digital objects to this div.

        Note that it is much more performant add multiple digital objects at
        once, rather than adding them one by one.

        :param digital_objects: Iterable of DigitalObjects that are added to
            this div.

        :raises ValueError: If any of the given DigitalObjects already exist in
            the div tree.
        """
        added_objects = set(digital_objects)
        existing_objects = self.root_div.nested_digital_objects
        common_objects_exist = not added_objects.isdisjoint(existing_objects)
        if common_objects_exist:
            raise ValueError(
                "Some of the given digital objects already exist in the div "
                "tree."
            )

        self.digital_objects |= added_objects

    def bundle_metadata(self):
        """Bundle shared non-technical metadata to structural map div
        recursively.

        If all child nodes share the same non-technical metadata, be it
        structural map div or digital object, delete that metadata from the
        child node and move it to the parent structural map div. The structural
        map div tree is traversed depth-first in post-order i.e. starting from
        the leaves and moving towards the root (self). This way the shared
        metadata can be propagated as close to the root (self) as possible.
        """
        # Apply this function recursively to child divs. If there are no child
        # divs left unvisited the rest of the function body is executed.
        for subdiv in self.divs:
            subdiv.bundle_metadata()

        children = list(self.digital_objects | self.divs)

        # Pick a child to check against the other children.
        child = children[0]
        shared_metadata = set(
            metadata for metadata in child.metadata
            if metadata.metadata_type != MetadataType.TECHNICAL
        )

        # Remove the unshared metadata. If 'shared_metadata' is empty it is not
        # shared and we can stop wasting time by returning immediately.
        for child in children:
            shared_metadata &= set(
                metadata for metadata in child.metadata
                if metadata.metadata_type != MetadataType.TECHNICAL
            )
            if not shared_metadata:
                return

        # Delete the shared metadata from all child nodes
        for child in children:
            child.metadata -= shared_metadata

        # Add the shared metadata to the parent node
        self.metadata |= shared_metadata


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

        :param root_div: StructuralMapDiv that is the root div of this
            structural map. The structural map has to have one and only one
            root div, but the root div can contain multiple nested divs.
        :param structural_map_type: String that identifies the type of
            structure represented by the structural map. For example, a
            structural map that represents a purely logical or intellectual
            structure could be described with value 'logical' whereas a
            structural map that represented a purely physical structure could
            be described with value 'physical'. However, the METS schema
            neither defines nor requires a common vocabulary for this
            attribute.
        :param label: String that describes the structural map to viewers of
            the METS document. This would be useful primarily where more than
            one structural map is provided for a single object. A descriptive
            label value, in that case, could clarify to users the purpose of
            each of the available structural maps.
        :param pid: Unique identifier of metadata, given as a string.
            Attribute value should be expressed in printable US-ASCII
            characters.
        :param pid_type: Identifier system used in the 'pid' attribute, given
            as a string.  Attribute is mandatory if the pid attribute is used.
            Attribute value should be expressed in printable US-ASCII
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
        if value is not None and not (value.isascii() and value.isprintable()):
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
        if value is not None and not (value.isascii() and value.isprintable()):
            raise ValueError(
                f"pid_type '{value}' contains characters that are not "
                "printable US-ASCII characters"
            )
        self._pid_type = value
