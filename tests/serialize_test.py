"""Tests for serialize.py."""
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest
from lxml import etree

from mets_builder import metadata, serialize
from mets_builder.digital_object import DigitalObject, DigitalObjectStream
from mets_builder.metadata.digital_provenance_event_metadata import \
    DigitalProvenanceEventMetadata, DigitalProvenanceAgentMetadata
from mets_builder.metadata.technical_video_metadata import \
    TechnicalVideoMetadata
from mets_builder.mets import METS, MetsProfile
from mets_builder.serialize import NAMESPACES, _SerializerState, _use_namespace
from mets_builder.structural_map import StructuralMap, StructuralMapDiv


@pytest.fixture()
def mets_object():
    """Get valid METS object."""
    mets = METS(
        mets_profile=MetsProfile.CULTURAL_HERITAGE,
        package_id="package_id",
        contract_id="urn:uuid:5b1afac8-4b51-4d2f-8c77-c7e9ddbdd019",
        creator_name="Mr. Foo",
        creator_type="INDIVIDUAL",
        content_id="content_id",
        label="label",
        create_date=datetime(2022, 1, 2, 3, 4, 5, 6, tzinfo=timezone.utc),
        last_mod_date=datetime(2022, 2, 3, 4, 5, 6, 7, tzinfo=timezone.utc),
        record_status="submission",
        catalog_version="1.7.6",
        specification="1.7.6",
    )
    mets.add_agent(
        name="Ms. Bar",
        other_role="Foo",
        other_type="Bar"
    )

    # digital objects and metadata
    md_1 = metadata.ImportedMetadata(
        data_path=Path("tests/data/imported_metadata.xml"),
        metadata_type="technical",
        metadata_format="other",
        other_format="PAS-special",
        format_version="1.0",
        identifier="_1"
    )
    do_1 = DigitalObject(
        sip_filepath="path/1",
        metadata=[md_1],
        identifier="digital_object_1"
    )

    md_2 = metadata.ImportedMetadata(
        data_path=Path("tests/data/imported_metadata.xml"),
        metadata_type="technical",
        metadata_format="other",
        other_format="PAS-special",
        format_version="1.0",
        identifier="_2"
    )
    do_2 = DigitalObject(
        sip_filepath="path/2",
        metadata=[md_2],
        identifier="digital_object_2"
    )

    # Structural map
    md_3 = metadata.ImportedMetadata(
        data_path=Path("tests/data/imported_metadata.xml"),
        metadata_type="descriptive",
        metadata_format="other",
        other_format="PAS-special",
        format_version="1.0",
        identifier="_3"
    )
    # Create structural map with the following div structure:
    # root_div (has metadata md_3)
    # --sub1
    # --sub2
    # ----subsub1 (has digital object do_1)
    # ----subsub2 (has digital object do_2)
    subsub1 = StructuralMapDiv(
        div_type="test_type",
        order=1,
        label="subsub1",
        orderlabel="i",
        digital_objects=[do_1]
    )
    subsub2 = StructuralMapDiv(
        div_type="test_type",
        order=2,
        label="subsub2",
        orderlabel="ii",
        digital_objects=[do_2]
    )
    sub1 = StructuralMapDiv(
        div_type="test_type",
        label="sub1"
    )
    sub2 = StructuralMapDiv(
        div_type="test_type",
        label="sub2",
        divs=[subsub1, subsub2]
    )
    root_div = StructuralMapDiv(
        div_type="test_type",
        divs=[sub1, sub2],
        metadata=[md_3]
    )
    # Add the map twice to test that multiple structural maps are supported
    structural_map_1 = StructuralMap(
        root_div=root_div,
        structural_map_type="test_structural_map",
        label="logical",
        pid="pid1",
        pid_type="pidtype"
    )
    structural_map_2 = StructuralMap(
        root_div=root_div,
        structural_map_type="test_structural_map",
        label="logical",
        pid="pid1",
        pid_type="pidtype"
    )
    mets.add_structural_map(structural_map_1)
    mets.add_structural_map(structural_map_2)

    # File references
    mets.generate_file_references()

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

    assert len(element) == 6
    assert element.find("mets:metsHdr", namespaces=NAMESPACES) is not None
    assert element.find("mets:dmdSec", namespaces=NAMESPACES) is not None
    assert element.find("mets:fileSec", namespaces=NAMESPACES) is not None
    assert len(element.findall("mets:structMap", namespaces=NAMESPACES)) == 2

    # Assert administrative metadata exists and contains other metadata than
    # descriptive metadata
    amd_sec = element.find("mets:amdSec", namespaces=NAMESPACES)
    assert amd_sec is not None
    assert len(amd_sec) == 2
    assert len(amd_sec.findall("mets:techMD", namespaces=NAMESPACES)) == 2


def test_parse_root_element(mets_object):
    """Test that METS root element is parsed correctly."""
    element = serialize._parse_mets_root_element(mets_object)

    # Attributes
    assert len(element.items()) == 8
    assert element.get("PROFILE") == (
        "http://digitalpreservation.fi/mets-profiles/cultural-heritage"
    )
    assert element.get("OBJID") == "package_id"
    assert element.get("LABEL") == "label"
    assert element.get(_use_namespace("fi", "CONTRACTID")) \
        == "urn:uuid:5b1afac8-4b51-4d2f-8c77-c7e9ddbdd019"
    assert element.get(_use_namespace("fi", "CONTENTID")) == "content_id"
    assert element.get(_use_namespace("fi", "CATALOG")) == "1.7.6"
    assert element.get(_use_namespace("fi", "SPECIFICATION")) == "1.7.6"
    assert element.get(_use_namespace("xsi", "schemaLocation")) == (
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
    state = _SerializerState()
    root_element = serialize._parse_metadata_element(data, state)

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
    state = _SerializerState()

    root_element = serialize._parse_metadata_element(data, state)
    assert root_element.get(_use_namespace("fi", "CREATED")) == "2011?"
    assert root_element.get("CREATED") is None


def test_parse_file_references_file_element(mets_object):
    """Test that a file in file references is parsed correctly."""
    md_do = metadata.ImportedMetadata(
        data_path=Path("tests/data/imported_metadata.xml"),
        metadata_type="technical",
        metadata_format="other",
        other_format="PAS-special",
        format_version="1.0",
        identifier="metadata-digital_object-id"
    )
    md_stream = metadata.ImportedMetadata(
        data_path=Path("tests/data/imported_metadata.xml"),
        metadata_type="technical",
        metadata_format="other",
        other_format="PAS-special",
        format_version="1.0",
        identifier="metadata-stream-id"
    )

    stream = DigitalObjectStream(metadata=[md_stream])
    do = DigitalObject(
        sip_filepath="path",
        metadata=[md_do],
        streams=[stream],
        identifier="digital_object-id"
    )

    state = _SerializerState()

    file_element = serialize._parse_file_references_file(do, state)

    assert file_element.tag == _use_namespace("mets", "file")
    assert file_element.get("ID") == "digital_object-id"
    assert file_element.get("ADMID") == "metadata-digital_object-id"
    file_location = file_element.find("mets:FLocat", namespaces=NAMESPACES)
    assert file_location is not None
    assert file_location.get("LOCTYPE") == "URL"
    assert file_location.get(_use_namespace("xlink", "href")) == "file:///path"
    assert file_location.get(_use_namespace("xlink", "type")) == "simple"
    stream = file_element.find("mets:stream", namespaces=NAMESPACES)
    assert stream is not None
    assert stream.get("ADMID") == "metadata-stream-id"


def test_written_file_references(mets_object):
    """Test that file references are written correctly.

    File elements themselves are tested more thoroughly on another test.
    """
    # Serialize the entire mets, then read it to lxml.etree._Element for
    # inspection
    serialized = serialize.to_xml_string(mets_object)
    element = etree.fromstring(serialized)
    filesec = element.find("mets:fileSec", namespaces=NAMESPACES)

    assert filesec is not None

    # Contains one group
    assert len(filesec) == 1
    group = filesec.find("mets:fileGrp", namespaces=NAMESPACES)
    assert group is not None

    # Group contains 2 files
    # Files are tested in a separate test
    assert len(group) == 2
    assert len(group.findall("mets:file", namespaces=NAMESPACES)) == 2


def test_written_structural_maps(mets_object):
    """Test that structural maps are written correctly."""
    # Serialize the entire mets, then read it to lxml.etree._Element for
    # inspection
    serialized = serialize.to_xml_string(mets_object)
    element = etree.fromstring(serialized)
    structmaps = element.findall("mets:structMap", namespaces=NAMESPACES)

    assert len(structmaps) == 2

    # The structmaps of the test mets_object are identical, so we can pick
    # either one for assertion
    structmap = structmaps.pop()

    # Root element
    assert structmap.tag == _use_namespace("mets", "structMap")
    assert structmap.get("TYPE") == "test_structural_map"
    assert structmap.get("LABEL") == "logical"
    assert structmap.get(_use_namespace("fi", "PID")) == "pid1"
    assert structmap.get(_use_namespace("fi", "PIDTYPE")) == "pidtype"

    # root div
    assert len(structmap) == 1
    root_div = structmap[0]
    assert root_div.tag == _use_namespace("mets", "div")
    assert root_div.get("TYPE") == "test_type"
    assert root_div.get("DMDID") == "_3"

    # sub divs
    assert len(root_div) == 2
    sub1 = root_div.findall("mets:div[@LABEL='sub1']", namespaces=NAMESPACES)
    assert len(sub1) == 1
    sub1 = sub1[0]
    assert sub1.get("TYPE") == "test_type"
    assert len(sub1) == 0

    sub2 = root_div.findall("mets:div[@LABEL='sub2']", namespaces=NAMESPACES)
    assert len(sub2) == 1
    sub2 = sub2[0]
    assert sub2.get("TYPE") == "test_type"
    assert len(sub2) == 2

    # subsub divs
    subsub1 = sub2.findall(
        "mets:div[@LABEL='subsub1']", namespaces=NAMESPACES
    )
    assert len(subsub1) == 1
    subsub1 = subsub1[0]
    assert subsub1.get("TYPE") == "test_type"
    assert subsub1.get("ORDER") == "1"
    assert subsub1.get("ORDERLABEL") == "i"
    assert len(subsub1) == 1
    fptr = subsub1.find("mets:fptr", namespaces=NAMESPACES)
    assert fptr.get("FILEID") == "digital_object_1"

    subsub2 = sub2.findall(
        "mets:div[@LABEL='subsub2']", namespaces=NAMESPACES
    )
    assert len(subsub2) == 1
    subsub2 = subsub2[0]
    assert subsub2.get("TYPE") == "test_type"
    assert subsub2.get("ORDER") == "2"
    assert subsub2.get("ORDERLABEL") == "ii"
    assert len(subsub2) == 1
    fptr = subsub2.find("mets:fptr", namespaces=NAMESPACES)
    assert fptr.get("FILEID") == "digital_object_2"


def test_metadata_identifier_generated():
    """
    Test that missing identifiers will be generated for technical metadata
    objects, and that said identifiers will be identical across objects
    that share the same metadata
    """
    state = _SerializerState()

    metadatas = []

    for _ in range(0, 4):
        metadatas.append(
            TechnicalVideoMetadata(
                identifier=None,
                duration="PT2H05M",
                data_rate="8",
                bits_per_sample="24",
                color="Color",
                codec_creator_app="SoundForge",
                codec_creator_app_version="10",
                codec_name="(:unav)",
                codec_quality="lossy",
                data_rate_mode="Fixed",
                frame_rate="24",
                pixels_horizontal="640",
                pixels_vertical="480",
                par="1.0",
                dar="4/3",
                sampling="4:2:2",
                signal_format="PAL",
                sound="No"
            )
        )

    # Change the third metadata to have slightly different metadata. This
    # ensures it will have a different identifier.
    metadatas[2].frame_rate = "48"

    # Fourth metadata has manually set identifier
    metadatas[3].identifier = "_bfb2a6fc-3df3-48ed-b8bc-d00fcafef00d"

    metadata_elems = []
    for metadata_ in metadatas:
        metadata_elems.append(
            serialize._parse_metadata_element(metadata_, state)
        )

    assert metadata_elems[0].attrib["ID"].startswith("_")
    uuid.UUID(metadata_elems[0].attrib["ID"][1:])

    # Metadata objects #1 and #2 have identical identifier due to sharing
    # same metadata
    assert metadata_elems[0].attrib["ID"] == metadata_elems[1].attrib["ID"]

    # Metadata object #3 was assigned different identifier due to different
    # metadata
    assert metadata_elems[2].attrib["ID"].startswith("_")
    uuid.UUID(metadata_elems[2].attrib["ID"][1:])
    assert metadata_elems[2].attrib["ID"] != metadata_elems[0].attrib["ID"]

    # Metadata object #4 uses its own identifier
    assert metadata_elems[3].attrib["ID"] == \
        "_bfb2a6fc-3df3-48ed-b8bc-d00fcafef00d"


def test_metadata_identifier_shared():
    """
    Test that missing identifiers will be generated for digital provenance
    event metadata objects, and that said identifiers will be identical across
    objects that share the same metadata
    """
    state = _SerializerState()

    events = []

    for _ in range(0, 3):
        events.append(
            DigitalProvenanceEventMetadata(
                event_type="calculation",
                event_datetime="2000-01-01T12:00:00",
                event_detail="Event detail",
                event_outcome="success",
                event_outcome_detail="Event outcome detail"
            )
        )

    for i in range(0, 2):
        events[i].link_agent_metadata(
            DigitalProvenanceAgentMetadata(
                agent_name="calculator",
                agent_type="software",
                agent_version="1.2.4"
            ),
            agent_role="executing program"
        )

    # The third event has a slightly different agent. This should be detected
    # later when generating the identifier
    events[2].link_agent_metadata(
        DigitalProvenanceAgentMetadata(
            agent_name="calculator",
            agent_type="software",
            agent_version="2.0"  # Different version
        ),
        agent_role="executing program"
    )

    event_elems = []
    for event_ in events:
        event_elems.append(
            serialize._parse_metadata_element(event_, state)
        )

    # Events 1 and 2 have same UUID, as they have the same content
    assert event_elems[0].attrib["ID"].startswith("_")
    uuid.UUID(event_elems[0].attrib["ID"][1:])
    assert event_elems[0].attrib["ID"] == event_elems[1].attrib["ID"]

    # Event 3 has a different UUID, because the referenced agent software
    # has a different version
    assert event_elems[1].attrib["ID"] != event_elems[2].attrib["ID"]

    # Agents also have their own identifiers which are proper UUIDs without
    # the underscore prefix
    agent_identifiers = [
        event_elem.xpath(
            "//premis:linkingAgentIdentifierValue",
            namespaces=NAMESPACES
        )[0].text for event_elem in event_elems
    ]

    # Like with events, the first and second agent have the same agent
    # identifiers
    uuid.UUID(agent_identifiers[0])
    assert agent_identifiers[0] == agent_identifiers[1]

    assert agent_identifiers[1] != agent_identifiers[2]

def test_metadata_created_generated():
    """
    Test that missing creation date for a metadata object will be generated
    at serialization time if not already provided
    """
    state = _SerializerState()

    data = {
        "identifier": None,
        "duration": "PT2H05M",
        "data_rate": "8",
        "bits_per_sample": "24",
        "color": "Color",
        "codec_creator_app": "SoundForge",
        "codec_creator_app_version": "10",
        "codec_name": "(:unav)",
        "codec_quality": "lossy",
        "data_rate_mode": "Fixed",
        "frame_rate": "24",
        "pixels_horizontal": "640",
        "pixels_vertical": "480",
        "par": "1.0",
        "dar": "4/3",
        "sampling": "4:2:2",
        "signal_format": "PAL",
        "sound": "No"
    }

    now = datetime.now(timezone.utc)

    # A has no creation date, this will be set automatically at time of
    # serialization
    metadata_a = TechnicalVideoMetadata(**data)

    # B has set creation date, this will be used by serializer
    metadata_b = TechnicalVideoMetadata(
        **{**data, **{"created": "2023-06-12"}}
    )

    elem_a = serialize._parse_metadata_element(metadata_a, state)

    # TODO: Replace this drudgery with `datetime.datetime.fromisoformat` once
    # we're on Python 3.7+. Or RHEL9, which ships Python 3.9.
    date_a = datetime.strptime(
        elem_a.attrib[f"{{{NAMESPACES['fi']}}}CREATED"],
        "%Y-%m-%dT%H:%M:%S.%f+00:00"
    )
    date_a = date_a.replace(tzinfo=timezone.utc)

    # Check that automatically generated creation date A is within two
    # seconds of the current time calculated at the start of test.
    delta = date_a - now
    assert abs(delta.total_seconds()) < 1

    elem_b = serialize._parse_metadata_element(metadata_b, state)

    # Creation date B is passed as-is
    assert elem_b.attrib[f"{{{NAMESPACES['fi']}}}CREATED"] == "2023-06-12"


def test_to_xml_string(mets_object):
    """Test that METS object can be serialized to XML string.

    The contents of the string is tested very lightly as the content is tested
    more thoroughly in other tests.
    """
    xml = serialize.to_xml_string(mets_object)
    assert b"<mets:mets" in xml
    assert b"</mets:mets>" in xml


def test_schema_validation(mets_object, tmp_path):
    """Test that METS document passes XML schema validation"""
    tool_path = shutil.which("check-xml-schema-features-3")

    if not tool_path:
        tool_path = shutil.which("check-xml-schema-features")

    if not tool_path:
        pytest.skip("dpres-ipt not installed, skipping METS validation test")

    path = tmp_path / "mets.xml"
    mets_object.write(path)

    result = subprocess.run(
        [tool_path, str(path)], check=False
    )
    assert result.returncode == 0


def test_schematron_validation(mets_object, tmp_path):
    """Test that METS document passes Schematron validation"""
    tool_path = shutil.which("check-xml-schematron-features-3")

    if not tool_path:
        tool_path = shutil.which("check-xml-schematron-features")

    if not tool_path:
        pytest.skip("dpres-ipt not installed, skipping METS validation test")

    path = tmp_path / "mets.xml"
    mets_object.write(path)

    result = subprocess.run(
        [
            tool_path,
            "-s", "/usr/share/dpres-xml-schemas/schematron/mets_root.sch",
            str(path)
        ], check=False
    )
    assert result.returncode == 0
