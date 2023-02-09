"""Module for serializing METS objects."""

from datetime import datetime
from io import BytesIO
from typing import TYPE_CHECKING

import mets as mets_elements
from lxml import etree

from mets_builder.digital_object import DigitalObject
from mets_builder.metadata import MetadataBase, MetadataType

# Prevent circular import caused by type hints with special
# typing.TYPE_CHECKING constant. See
# https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING for more
# info
if TYPE_CHECKING:
    from mets_builder.mets import METS

_NAMESPACES = {
    "mets": "http://www.loc.gov/METS/",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "premis": "info:lc/xmlns/premis-v2",
    "fi": "http://digitalpreservation.fi/schemas/mets/fi-extensions",
    "xlink": "http://www.w3.org/1999/xlink",
    "mix": "http://www.loc.gov/mix/v20",
    "ead3": "http://ead3.archivists.org/schema/",
    "addml": "http://www.arkivverket.no/standarder/addml",
    "audiomd": "http://www.loc.gov/audioMD/",
    "videomd": "http://www.loc.gov/videoMD/"
}
_METS_FI_SCHEMA = "http://digitalpreservation.fi/schemas/mets/mets.xsd"


def _use_namespace(namespace, attribute):
    """Get a string prepended with a namespace prefix."""
    return f"{{{_NAMESPACES[namespace]}}}{attribute}"


def _parse_mets_root_element(mets):
    """Parse root element for given METS object.

    :param METS mets: METS object

    :returns: METS root element (mets:mets) as lxml.etree._Element
    """
    # Create the root element
    mets_root = mets_elements.mets(
        profile=mets.mets_profile.value,
        objid=mets.package_id,
        label=mets.label,
        namespaces=_NAMESPACES
    )

    # Set Finnish national METS schema specific attributes to the root element
    mets_root.set(_use_namespace("fi", "CONTRACTID"), mets.contract_id)
    if mets.content_id:
        mets_root.set(_use_namespace("fi", "CONTENTID"), mets.content_id)
    if mets.catalog_version:
        mets_root.set(_use_namespace("fi", "CATALOG"), mets.catalog_version)
    if mets.specification:
        mets_root.set(
            _use_namespace("fi", "SPECIFICATION"), mets.specification
        )

    # Delete standard METS schema location set by mets library
    del mets_root.attrib[_use_namespace("xsi", "schemaLocation")]

    # Set Finnish national METS schema location to the root element
    mets_root.set(
        _use_namespace("xsi", "schemaLocation"),
        f"{_NAMESPACES['mets']} {_METS_FI_SCHEMA}"
    )

    return mets_root


def _parse_mets_header(mets):
    """Parse metsHdr for given METS object.

    :param METS mets: METS object

    :returns: METS header (mets:metsHdr) as lxml.etree._Element
    """
    # Parse agents
    agents = []
    for agent in mets.agents:
        agent_element = mets_elements.agent(
            organisation_name=agent.name,
            agent_role=agent.agent_role.value,
            otherrole=agent.other_role,
            agent_type=agent.agent_type.value,
            othertype=agent.other_type
        )
        agents.append(agent_element)

    # Format last_mod_date if it is set
    last_mod_date = mets.last_mod_date
    if last_mod_date is not None:
        last_mod_date = last_mod_date.isoformat(timespec="seconds")

    # Create metsHdr element
    mets_header = mets_elements.metshdr(
        create_date=mets.create_date.isoformat(timespec="seconds"),
        last_mod_date=last_mod_date,
        record_status=mets.record_status.value,
        agents=agents
    )

    return mets_header


def _parse_metadata_element(metadata: MetadataBase):
    """Parse given metadata object.

    :param MetadataBase metadata: The metadata object that should be parsed.

    :returns: The metadata wrapped in the correct base element (dmdSec, techMD
        etc.) as lxml.etree._Element
    """
    # Serialize metadata
    serialized_metadata = metadata.to_xml_element_tree()

    # Metadata has to be wrapped in mdWrap and xmlData elements
    xml_data = mets_elements.xmldata(child_elements=[serialized_metadata])
    md_wrap = mets_elements.mdwrap(
        mdtype=metadata.metadata_format.value,
        mdtypeversion=metadata.format_version,
        othermdtype=metadata.other_format,
        child_elements=[xml_data]
    )

    # Format create time and determine whether the time is an estimation (it
    # was given as a string)
    created = metadata.created
    created_is_estimation = True
    if isinstance(metadata.created, datetime):
        created = metadata.created.isoformat(timespec="seconds")
        created_is_estimation = False

    # Determine base element (techMD, dmdSec etc.)
    if metadata.metadata_type == MetadataType.TECHNICAL:
        element_builder_function = mets_elements.techmd
    elif metadata.metadata_type == MetadataType.DIGITAL_PROVENANCE:
        element_builder_function = mets_elements.digiprovmd
    elif metadata.metadata_type == MetadataType.DESCRIPTIVE:
        element_builder_function = mets_elements.dmdsec

    # Create element
    metadata_element = element_builder_function(
        element_id=metadata.identifier,
        created_date=created,
        child_elements=[md_wrap]
    )

    # If created is an estimated time, it has to be declared using Finnish
    # national METS namespace
    if created_is_estimation:
        # delete CREATED attribute from the metadata element
        del metadata_element.attrib["CREATED"]
        # add it back with fi namespace
        metadata_element.set(_use_namespace("fi", "CREATED"), created)

    return metadata_element


def _write_descriptive_metadata(xml, mets):
    """Write descriptive metadata to the given XML file."""
    descriptive_metadata = iter(
        metadata for metadata in mets.metadata
        if metadata.is_descriptive
    )
    for metadata in descriptive_metadata:
        metadata_element = _parse_metadata_element(metadata)
        xml.write(metadata_element)


def _write_administrative_metadata(xml, mets):
    """Write administrative metadata to the given XML file."""
    administrative_metadata = iter(
        metadata for metadata in mets.metadata
        if metadata.is_administrative
    )
    amdsec = mets_elements.amdsec()
    with xml.element(amdsec.tag):
        for metadata in administrative_metadata:
            metadata_element = _parse_metadata_element(metadata)
            xml.write(metadata_element)


def _parse_file_references_file(digital_object: DigitalObject):
    """Parse given digital object as file element in file references."""
    # Streams
    streams = []
    for stream in digital_object.streams:
        administrative_metadata_identifiers = [
            metadata.identifier for metadata in stream.metadata
            if metadata.is_administrative
        ]
        streams.append(
            mets_elements.stream(administrative_metadata_identifiers)
        )

    # File
    administrative_metadata_identifiers = [
        metadata.identifier for metadata in digital_object.metadata
        if metadata.is_administrative
    ]
    digital_object_element = mets_elements.file_elem(
        file_id=digital_object.identifier,
        admid_elements=administrative_metadata_identifiers,
        loctype="URL",
        xlink_href=f"file://{digital_object.sip_filepath}",
        xlink_type="simple"
    )
    for stream in streams:
        digital_object_element.append(stream)

    return digital_object_element


def _write_file_references(xml, file_references):
    """Write file references to the given XML file."""
    file_references_root = mets_elements.filesec()
    with xml.element(file_references_root.tag, file_references_root.attrib):
        for group in file_references.file_groups:
            group_root = mets_elements.filegrp(use=group.use)
            with xml.element(group_root.tag, group_root.attrib):
                for digital_object in group.digital_objects:
                    xml.write(_parse_file_references_file(digital_object))


def _write_structural_map_div(xml, div):
    """Write a structural map div and recursively its nested divs to the given
    xml file.
    """
    administrative_metadata_identifiers = [
        metadata.identifier for metadata in div.metadata
        if metadata.is_administrative
    ]
    descriptive_metadata_identifiers = [
        metadata.identifier for metadata in div.metadata
        if metadata.is_descriptive
    ]
    file_pointer_elements = [
        mets_elements.fptr(digital_object.identifier)
        for digital_object in div.digital_objects
    ]

    # Cast order to string
    order = div.order
    if div.order is not None:
        order = str(div.order)

    div_element = mets_elements.div(
        type_attr=div.div_type,
        order=order,
        label=div.label,
        orderlabel=div.orderlabel,
        dmdid=descriptive_metadata_identifiers,
        admid=administrative_metadata_identifiers
    )
    with xml.element(div_element.tag, div_element.attrib):
        for element in file_pointer_elements:
            xml.write(element)
        for nested_div in div.divs:
            _write_structural_map_div(xml, nested_div)


def _write_structural_map(xml, structural_map):
    """Write structural map to the given XML file."""
    structural_map_root = mets_elements.structmap(
        type_attr=structural_map.structural_map_type,
        label=structural_map.label
    )

    # Set Finnish national METS schema specific attributes to the root element
    if structural_map.pid:
        structural_map_root.set(
            _use_namespace("fi", "PID"), structural_map.pid
        )
    if structural_map.pid_type:
        structural_map_root.set(
            _use_namespace("fi", "PIDTYPE"), structural_map.pid_type
        )

    with xml.element(structural_map_root.tag, structural_map_root.attrib):
        _write_structural_map_div(xml, structural_map.root_div)


def _write_mets(mets, output_file):
    """Write METS object to file serialized as XML.

    :param METS mets: METS object to serialize
    :param BytesIO, str output_file: File to write the serialized METS to. It
        can be given as a BytesIO file object or as path to the output file. If
        BytesIO is given, the caller should take care of closing the file
        themselves.

    :returns: The given output_file.
    """
    # Use incremental XML generation with context managers.
    # This saves memory by writing elements incrementally rather than
    # constructing the entire tree in memory before writing
    with etree.xmlfile(output_file, encoding="utf-8") as xml:

        # METS root element
        mets_root = _parse_mets_root_element(mets)
        with xml.element(mets_root.tag, mets_root.attrib, mets_root.nsmap):

            # METS Header
            xml.write(_parse_mets_header(mets))

            # Descriptive metadata
            _write_descriptive_metadata(xml, mets)

            # Administrative metadata
            _write_administrative_metadata(xml, mets)

            # File references
            if mets.file_references:
                _write_file_references(xml, mets.file_references)

            # Structural maps
            for structural_map in mets.structural_maps:
                _write_structural_map(xml, structural_map)

    return output_file


def to_xml_string(mets: "METS") -> bytes:
    """Serialize METS object to XML string.

    :param METS mets: METS object

    :returns: Given METS object as XML-formatted byte string.
    """
    output_file = BytesIO()
    result = _write_mets(mets, output_file).getvalue()
    output_file.close()

    return result


def write_to_file(mets: "METS", output_filepath: str) -> None:
    """Serialize METS object to XML and write to given file path."""
    _write_mets(mets, output_filepath)
