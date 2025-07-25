import pytest
from mets_builder.metadata.mets_metadata import MetsMetadataType
from mets_builder.metadata.metadata import MetadataFormat as mdf


def test_valid_metadata_without_other_format():
    obj = MetsMetadataType(
        uri="http://purl.org/dc/elements/1.1",
        mdt_format=mdf.DC,
        version="8.3",
    )
    assert obj.uri == "http://purl.org/dc/elements/1.1"
    assert obj.mdt_format == mdf.DC
    assert obj.version == "8.3"
    assert obj.other_format is None


def test_valid_metadata_with_other_format():
    obj = MetsMetadataType(
        uri="http://datacite.org/schema/kernel-4",
        mdt_format=mdf.OTHER,
        other_format="DATACITE",
        version="4.3",
    )
    assert obj.mdt_format == mdf.OTHER
    assert obj.other_format == "DATACITE"


def test_missing_required_fields_raises_assertion():
    with pytest.raises(TypeError):
        # uri missing
        MetsMetadataType(
            mdt_format=mdf.OTHER,
            other_format="DATACITE",
            version="4.3",
        )


def test_format_other_without_other_format_raises_value_error():
    with pytest.raises(ValueError):
        MetsMetadataType(
            uri="http://datacite.org/schema/kernel-4",
            mdt_format=mdf.OTHER,
            version="4.3",
        )
