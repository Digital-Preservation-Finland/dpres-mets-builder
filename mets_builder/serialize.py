"""Module for serializing METS objects."""
from typing import TYPE_CHECKING

import lxml.etree
import mets as mets_elements
import xml_helpers

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


def to_xml_string(mets: "METS") -> bytes:
    """Serialize METS object to XML string.

    :param METS mets: METS object

    :returns: Given METS object as XML-formatted byte string.
    """
    parsed_mets = _parse_mets(mets)
    return xml_helpers.utils.serialize(parsed_mets)
