"""Tests for serialize.py."""
from datetime import datetime
from datetime import timezone

import pytest

from mets_builder.mets import METS
from mets_builder import serialize
from mets_builder.serialize import _NAMESPACES


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

    return mets


def test_parse_mets(mets_object):
    """Test parsing the METS object.

    This function only tests that the METS document has all the intended
    first-level elements, as the other functions test the contents of the
    elements more thoroughly.
    """
    element = serialize._parse_mets(mets_object)
    subelements = list(element)

    assert len(subelements) == 1
    assert element.find("mets:metsHdr", namespaces=_NAMESPACES) is not None


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


def test_to_xml_string(mets_object):
    """Test that METS object can be serialized to XML string.

    The contents of the string is tested very lightly as the content is tested
    more thoroughly in other tests.
    """
    xml = serialize.to_xml_string(mets_object)
    assert b"<mets:mets" in xml
    assert b"</mets:mets>" in xml
