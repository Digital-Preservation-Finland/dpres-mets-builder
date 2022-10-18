from file_scraper.scraper import Scraper
from lxml import etree

from mets_builder.metadata import TechnicalImageMetadata


def test_technical_image_metadata_using_file_scraper_output():
    """Test that it is possible to create technical image metadata by providing
    file-scraper output as is to the TechnicalImageMetadata class.
    """
    scraper = Scraper(
        "tests/integration_tests/data/valid_1.01_icc_sRGB_profile.jpg"
    )
    scraper.scrape()
    data = TechnicalImageMetadata(**scraper.streams[0])

    result = etree.tostring(
        data.to_xml(), pretty_print=True, encoding="UTF-8"
    )

    with open(
        "tests/integration_tests/data/expected_technical_image_metadata.xml",
        "rb"
    ) as _file:
        expected_xml = _file.read()

    assert result == expected_xml
