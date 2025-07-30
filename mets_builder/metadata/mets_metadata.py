from __future__ import annotations
from mets_builder.metadata.metadata import MetadataFormat as mdf
from mets_builder.defaults import UNAV


class MetsMetadataType:
    def __init__(
        self, *,
        uri: str,
        mdt_format: mdf,
        version: str,
        other_format: str | None = None,
    ):
        if other_format:
            mdt_format = mdf.OTHER
        if mdt_format == mdf.OTHER and not other_format:
            raise ValueError(
                "'metadata_format' is 'OTHER' but 'other_format' is "
                "not given.")
        if version is None or version == "":
            version = UNAV
        self.uri = uri
        self.mdt_format = mdt_format
        self.version = version
        self.other_format = other_format


METS_MDTYPES: dict[str, MetsMetadataType] = {
    "http://purl.org/dc/elements/1.1": MetsMetadataType(
        uri="http://purl.org/dc/elements/1.1",
        mdt_format=mdf.DC,
        version="2008"
    ),
    "http://www.loc.gov/MARC21/slim": MetsMetadataType(
        uri="http://www.loc.gov/MARC21/slim",
        mdt_format=mdf.MARC,
        version="marcxml=1.2; marc=marc21",
    ),
    "http://www.loc.gov/mods/v3": MetsMetadataType(
        uri="http://www.loc.gov/mods/v3",
        mdt_format=mdf.MODS,
        version="3.8"
    ),
    "urn:isbn:1-931666-22-9": MetsMetadataType(
        uri="urn:isbn:1-931666-22-9",
        mdt_format=mdf.EAD,
        version="2002"
    ),
    "http://ead3.archivists.org/schema": MetsMetadataType(
        uri="http://ead3.archivists.org/schema",
        mdt_format=mdf.OTHER,
        other_format="EAD3",
        version="1.1.1",
    ),
    "urn:isbn:1-931666-33-4": MetsMetadataType(
        uri="urn:isbn:1-931666-33-4",
        mdt_format=mdf.EAC_CPF,
        version="2010_revised",
    ),
    "https://archivists.org/ns/eac/v2": MetsMetadataType(
        uri="https://archivists.org/ns/eac/v2",
        mdt_format=mdf.EAC_CPF,
        version="2.0",
    ),
    "http://www.lido-schema.org": MetsMetadataType(
        uri="http://www.lido-schema.org",
        mdt_format=mdf.LIDO,
        version="1.1"
    ),
    "ddi:instance:3_3": MetsMetadataType(
        uri="ddi:instance:3_3",
        mdt_format=mdf.DDI,
        version="3.3"),
    "ddi:instance:3_2": MetsMetadataType(
        uri="ddi:instance:3_2",
        mdt_format=mdf.DDI,
        version="3.2"),
    "ddi:instance:3_1": MetsMetadataType(
        uri="ddi:instance:3_1",
        mdt_format=mdf.DDI,
        version="3.1"),
    "ddi:codebook:2_5": MetsMetadataType(
        uri="ddi:codebook:2_5",
        mdt_format=mdf.DDI,
        version="2.5.1"),
    "http://www.icpsr.umich.edu/DDI": MetsMetadataType(
        uri="http://www.icpsr.umich.edu/DDI",
        mdt_format=mdf.DDI,
        version="2.1"
    ),
    "http://www.vraweb.org/vracore4.htm": MetsMetadataType(
        uri="http://www.vraweb.org/vracore4.htm",
        mdt_format=mdf.VRA,
        version="4.0"
    ),
    "http://www.arkivverket.no/standarder/addml": MetsMetadataType(
        uri="http://www.arkivverket.no/standarder/addml",
        mdt_format=mdf.OTHER,
        other_format="ADDML",
        version="8.3",
    ),
    "http://datacite.org/schema/kernel-4": MetsMetadataType(
        uri="http://datacite.org/schema/kernel-4",
        mdt_format=mdf.OTHER,
        other_format="DATACITE",
        version="4.3",
    ),
    "http://www.loc.gov/audioMD": MetsMetadataType(
        uri="http://www.loc.gov/audioMD",
        mdt_format=mdf.OTHER,
        other_format="AudioMD",
        version="2.0",
    ),
    "http://www.loc.gov/videoMD": MetsMetadataType(
        uri="http://www.loc.gov/videoMD",
        mdt_format=mdf.OTHER,
        other_format="VideoMD",
        version="2.0",
    ),
    "urn:ebu:metadata-schema:ebucore": MetsMetadataType(
        uri="urn:ebu:metadata-schema:ebucore",
        mdt_format=mdf.OTHER,
        other_format="EBUCORE",
        version="1.10",
    ),
}
