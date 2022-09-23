"""Tests for serialize.py."""
from datetime import datetime, timezone
from pathlib import Path

import pytest
from lxml import etree

from mets_builder import metadata, serialize
from mets_builder.mets import METS
from mets_builder.serialize import _NAMESPACES, _use_namespace


@pytest.fixture()
def mets_object():
    """Get valid METS object."""
    mets = METS(
        mets_profile=(
            "https://digitalpreservation.fi/mets-profiles/cultural-heritage"
        ),
        package_id="package_id",
        contract_id="contract_id",
        creator_name="Mr. Foo",
        creator_type="INDIVIDUAL",
        content_id="content_id",
        label="label",
        create_date=datetime(2022, 1, 2, 3, 4, 5, 6, tzinfo=timezone.utc),
        last_mod_date=datetime(2022, 2, 3, 4, 5, 6, 7, tzinfo=timezone.utc),
        record_status="submission",
        catalog_version="1.0",
        specification="2.0",
    )
    mets.add_agent(
        name="Ms. Bar",
        other_role="Foo",
        other_type="Bar"
    )

    md_1 = metadata.ImportedMetadata(
        data_path=Path("tests/data/imported_metadata.xml"),
        metadata_type="descriptive",
        metadata_format="other",
        other_format="PAS-special",
        format_version="1.0",
        identifier="1"
    )
    md_2 = metadata.ImportedMetadata(
        data_path=Path("tests/data/imported_metadata.xml"),
        metadata_type="technical",
        metadata_format="other",
        other_format="PAS-special",
        format_version="1.0",
        identifier="2"
    )
    mets.add_metadata(md_1)
    mets.add_metadata(md_2)

    return mets


def test_parse_mets(mets_object):
    """Test parsing the METS object.

    This function only tests that the METS document has all the intended
    first-level elements, as the other functions test the contents of the
    elements more thoroughly.
    """
    # Serialize the entire mets, then read it to lxml.etree._Element for
    # inspection
    serialized = serialize.to_xml_string(mets_object)
    element = etree.fromstring(serialized)

    assert len(element) == 3
    assert element.find("mets:metsHdr", namespaces=_NAMESPACES) is not None
    assert element.find("mets:dmdSec", namespaces=_NAMESPACES) is not None

    # Assert administrative metadata exists and contains other metadata than
    # descriptive metadata
    amd_sec = element.find("mets:amdSec", namespaces=_NAMESPACES)
    assert amd_sec is not None
    assert len(amd_sec) == 1
    assert amd_sec.find("mets:techMD", namespaces=_NAMESPACES) is not None


def test_parse_root_element(mets_object):
    """Test that METS root element is parsed correctly."""
    element = serialize._parse_mets_root_element(mets_object)

    # Attributes
    assert len(element.items()) == 8
    assert element.get("PROFILE") == (
        "https://digitalpreservation.fi/mets-profiles/cultural-heritage"
    )
    assert element.get("OBJID") == "package_id"
    assert element.get("LABEL") == "label"
    assert element.get(f"{{{_NAMESPACES['fi']}}}CONTRACTID") == "contract_id"
    assert element.get(f"{{{_NAMESPACES['fi']}}}CONTENTID") == "content_id"
    assert element.get(f"{{{_NAMESPACES['fi']}}}CATALOG") == "1.0"
    assert element.get(f"{{{_NAMESPACES['fi']}}}SPECIFICATION") == "2.0"
    assert element.get(f"{{{_NAMESPACES['xsi']}}}schemaLocation") == (
        "http://www.loc.gov/METS/ "
        "http://digitalpreservation.fi/schemas/mets/mets.xsd"
    )


def test_parse_mets_header(mets_object):
    """Test that metsHdr is parsed correctly."""
    element = serialize._parse_mets_header(mets_object)

    # Attributes
    assert len(element.items()) == 3

    # Times are expressed with the resolution of a second
    assert element.get("CREATEDATE") == "2022-01-02T03:04:05+00:00"
    assert element.get("LASTMODDATE") == "2022-02-03T04:05:06+00:00"

    assert element.get("RECORDSTATUS") == "submission"

    # Agents
    agents = list(element)
    assert len(agents) == 2

    assert len(agents[0].items()) == 2
    assert agents[0].get("ROLE") == "CREATOR"
    assert agents[0].get("TYPE") == "INDIVIDUAL"

    # The agent should only contain one subelement containing the name
    name_element = list(agents[0])
    assert len(name_element) == 1
    assert name_element[0].text == "Mr. Foo"

    # Second agent has unconventional role and type, so ROLE and TYPE
    # attributes should be "OTHER" and actual values set in OTHERROLE and
    # OTHERTYPE
    assert len(agents[1].items()) == 4
    assert agents[1].get("ROLE") == "OTHER"
    assert agents[1].get("OTHERROLE") == "Foo"
    assert agents[1].get("TYPE") == "OTHER"
    assert agents[1].get("OTHERTYPE") == "Bar"
    name_element = list(agents[1])
    assert len(name_element) == 1
    assert name_element[0].text == "Ms. Bar"


@pytest.mark.parametrize(
    ["metadata_type", "root_element_tag"],
    [
        (metadata.MetadataType.DESCRIPTIVE, "dmdSec"),
        (metadata.MetadataType.TECHNICAL, "techMD"),
        (metadata.MetadataType.DIGITAL_PROVENANCE, "digiprovMD")
    ]
)
def test_parse_metadata_element(metadata_type, root_element_tag):
    """Test that a metadata object is parsed correctly."""
    data = metadata.ImportedMetadata(
        data_path=Path("tests/data/imported_metadata.xml"),
        metadata_type=metadata_type,
        metadata_format="other",
        other_format="PAS-special",
        format_version="1.0",
        identifier="identifier",
        created=datetime(2000, 1, 2, 3, 4, 5, 6, tzinfo=timezone.utc)
    )
    root_element = serialize._parse_metadata_element(data)

    # The root element tag depends on metadata type
    assert root_element.tag == _use_namespace("mets", root_element_tag)
    assert len(root_element.items()) == 2
    assert root_element.get("ID") == "identifier"
    assert root_element.get("CREATED") == "2000-01-02T03:04:05+00:00"

    # The root element wraps mdWrap element
    assert len(root_element) == 1
    md_wrap = root_element[0]
    assert md_wrap.tag == _use_namespace("mets", "mdWrap")
    assert len(md_wrap.items()) == 3
    assert md_wrap.get("MDTYPE") == "OTHER"
    assert md_wrap.get("MDTYPEVERSION") == "1.0"
    assert md_wrap.get("OTHERMDTYPE") == "PAS-special"

    # Which wraps xmlData element
    assert len(md_wrap) == 1
    xml_data = md_wrap[0]
    assert xml_data.tag == _use_namespace("mets", "xmlData")

    # Which wraps the actual metadata
    assert len(xml_data) == 1
    metadata_element = xml_data[0]

    # The metadata content is
    # <root>
    #   <sub1></sub1>
    #   <sub2></sub2>
    # </root>
    assert metadata_element.tag == "root"
    assert len(metadata_element) == 2
    assert metadata_element[0].tag == "sub1"
    assert metadata_element[1].tag == "sub2"


def test_parse_metadata_with_estimated_create_time():
    """Test that if estimated create time is given to metadata, it is written
    using fi:CREATED attribute and CREATED attribute does not exist.
    """
    data = metadata.ImportedMetadata(
        data_path=Path("tests/data/imported_metadata.xml"),
        metadata_type="technical",
        metadata_format="NISOIMG",
        format_version="1.0",
        created="2011?"
    )
    root_element = serialize._parse_metadata_element(data)
    assert root_element.get(_use_namespace("fi", "CREATED")) == "2011?"
    assert root_element.get("CREATED") is None


def test_to_xml_string(mets_object):
    """Test that METS object can be serialized to XML string.

    The contents of the string is tested very lightly as the content is tested
    more thoroughly in other tests.
    """
    xml = serialize.to_xml_string(mets_object)
    assert b"<mets:mets" in xml
    assert b"</mets:mets>" in xml
