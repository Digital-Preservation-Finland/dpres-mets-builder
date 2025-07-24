from mets_builder.metadata.metadata import MetadataFormat as mdf


class MetsMetadataType:
    def __init__(
        self,
        uri: str = None,
        format: mdf = None,
        version: str = None,
        other_format: str = None,
    ):
        assert None not in [uri, format, version]
        if other_format:
            format = mdf.OTHER
        if format == mdf.OTHER and not other_format:
            raise ValueError(
                "'metadata_format' is 'OTHER' but 'other_format' is "
                "not given.")
        self.uri = uri
        self.format = format
        self.version = version
        self.other_format = other_format


# Uri must be unique
METS_MDTYPES_LIST = [
    MetsMetadataType(
        uri="http://purl.org/dc/elements/1.1",
        format=mdf.DC,
        version="2008"
    ),
    MetsMetadataType(
        uri="http://www.loc.gov/MARC21/slim",
        format=mdf.MARC,
        version="marcxml=1.2; marc=marc21",
    ),
    MetsMetadataType(
        uri="http://www.loc.gov/mods/v3",
        format=mdf.MODS,
        version="3.8"
    ),
    MetsMetadataType(
        uri="urn:isbn:1-931666-22-9",
        format=mdf.EAD,
        version="2002"
    ),
    MetsMetadataType(
        uri="http://ead3.archivists.org/schema",
        format=mdf.OTHER,
        other_format="EAD3",
        version="1.1.1",
    ),
    MetsMetadataType(
        uri="urn:isbn:1-931666-33-4",
        format=mdf.EAC_CPF,
        version="2010_revised",
    ),
    MetsMetadataType(
        uri="https://archivists.org/ns/eac/v2",
        format=mdf.EAC_CPF,
        version="2.0",
    ),
    MetsMetadataType(
        uri="http://www.lido-schema.org",
        format=mdf.LIDO,
        version="1.1"
    ),
    MetsMetadataType(
        uri="ddi:instance:3_3",
        format=mdf.DDI,
        version="3.3"),
    MetsMetadataType(
        uri="ddi:instance:3_2",
        format=mdf.DDI,
        version="3.2"),
    MetsMetadataType(
        uri="ddi:instance:3_1",
        format=mdf.DDI,
        version="3.1"),
    MetsMetadataType(
        uri="ddi:codebook:2_5",
        format=mdf.DDI,
        version="2.5.1"),
    MetsMetadataType(
        uri="http://www.icpsr.umich.edu/DDI",
        format=mdf.DDI,
        version="2.1"
    ),
    MetsMetadataType(
        uri="http://www.vraweb.org/vracore4.htm",
        format=mdf.VRA,
        version="4.0"
    ),
    MetsMetadataType(
        uri="http://www.arkivverket.no/standarder/addml",
        format=mdf.OTHER,
        other_format="ADDML",
        version="8.3",
    ),
    MetsMetadataType(
        uri="http://datacite.org/schema/kernel-4",
        format=mdf.OTHER,
        other_format="DATACITE",
        version="4.3",
    ),
    MetsMetadataType(
        uri="http://www.loc.gov/audioMD",
        format=mdf.OTHER,
        other_format="AudioMD",
        version="2.0",
    ),
    MetsMetadataType(
        uri="http://www.loc.gov/videoMD",
        format=mdf.OTHER,
        other_format="VideoMD",
        version="2.0",
    ),
    MetsMetadataType(
        uri="urn:ebu:metadata-schema:ebucore",
        format=mdf.OTHER,
        other_format="EBUCORE",
        version="1.10",
    ),
]

# Mets metadata formatted as a dictionary with unique uri as the key value.
METS_MDTYPES = {
    mdt.uri:
        {
            'format':       mdt.format,
            'other_format':  mdt.other_format,
            'version':      mdt.version
        } for mdt in METS_MDTYPES_LIST
}
