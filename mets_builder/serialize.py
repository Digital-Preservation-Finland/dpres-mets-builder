"""Module for serializing METS objects."""
from datetime import datetime
from typing import TYPE_CHECKING

import lxml.etree
import mets as mets_elements
import xml_helpers

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


def _parse_mets(mets):
    """Parse METS XML tree for given METS object.

    :param METS mets: METS object

    :returns: Root element (mets:mets) of the fully parsed METS object as
        lxml.etree._Element
    """
    mets_root = _parse_mets_root_element(mets)
    mets_root.append(_parse_mets_header(mets))
    _append_metadata(mets_root, mets)

    return mets_root


def _parse_mets_root_element(mets):
    """Parse root element for given METS object.

    :param METS mets: METS object

    :returns: METS root element (mets:mets) as lxml.etree._Element
    """
    # Create the root element
    mets_root = mets_elements.mets(
        profile=mets.mets_profile,
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

    # Remove unused namespaces
    lxml.etree.cleanup_namespaces(mets_root)

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
            agent_role=agent.role.value,
            otherrole=agent.other_role,
            agent_type=agent.type.value,
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
        record_status=mets.record_status,
        agents=agents
    )

    return mets_header


def _append_metadata(mets_root, mets):
    """Parse metadata from METS object and append them to a lxml element.

    :param lxml.etree._Element mets_root: Element to which metadata are
        appended
    :param METS mets: The METS object
    """
    amdsec_metadata = []

    for metadata in mets.metadata:
        parsed_metadata = _parse_metadata_element(metadata)
        if metadata.metadata_type == MetadataType.DESCRIPTIVE:
            # Descriptive metadata are added to mets root element
            mets_root.append(parsed_metadata)
        else:
            # Other metadata are added to administrative metadata element
            # (amdSec)
            amdsec_metadata.append(parsed_metadata)

    amdsec = mets_elements.amdsec(child_elements=amdsec_metadata)
    mets_root.append(amdsec)


def _parse_metadata_element(metadata: MetadataBase):
    """Parse given metadata object.

    :param MetadataBase metadata: The metadata object that should be parsed.

    :returns: The metadata wrapped in the correct base element (dmdSec, techMD
        etc.) as lxml.etree._Element
    """
    # Serialize metadata
    serialized_metadata = metadata.serialize()

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


def to_xml_string(mets: "METS") -> bytes:
    """Serialize METS object to XML string.

    :param METS mets: METS object

    :returns: Given METS object as XML-formatted byte string.
    """
    parsed_mets = _parse_mets(mets)
    return xml_helpers.utils.serialize(parsed_mets)
