"""Tests for mets.py."""
import pytest

from mets_builder import METS


def test_invalid_mets_profile():
    """Test that initializing METS instance with invalid METS profile raises
    ValueError.
    """
    with pytest.raises(ValueError) as error:
        METS(
            mets_profile="invalid",
            package_id="package_id",
            contract_id="contract_id",
            creator_name="Mr. Foo"
        )
    assert str(error.value) == (
        "'invalid' is not a valid value for mets_profile. "
        "Value must be one of "
        "['https://digitalpreservation.fi/mets-profiles/cultural-heritage', "
        "'https://digitalpreservation.fi/mets-profiles/research-data']"
    )


@pytest.mark.parametrize(
    ["invalid_value", "error_message"],
    [
        (None, "package_id can not be None"),
        ("ä", ("package_id 'ä' contains characters that are not printable "
               "US-ASCII characters"))
    ]
)
def test_invalid_package_id(invalid_value, error_message):
    """Test that initializing METS instance with invalid package_id raises
    ValueError.
    """
    with pytest.raises(ValueError) as error:
        METS(
            mets_profile=(
                "https://digitalpreservation.fi/mets-profiles/"
                "cultural-heritage"
            ),
            package_id=invalid_value,
            contract_id="contract_id",
            creator_name="Mr. Foo"
        )
    assert str(error.value) == error_message


@pytest.mark.parametrize(
    ["invalid_value", "error_message"],
    [
        (None, "contract_id can not be None"),
        ("ä", ("contract_id 'ä' contains characters that are not printable "
               "US-ASCII characters"))
    ]
)
def test_invalid_contract_id(invalid_value, error_message):
    """Test that initializing METS instance with invalid contract_id raises
    ValueError.
    """
    with pytest.raises(ValueError) as error:
        METS(
            mets_profile=(
                "https://digitalpreservation.fi/mets-profiles/"
                "cultural-heritage"
            ),
            package_id="package_id",
            contract_id=invalid_value,
            creator_name="Mr. Foo"
        )
    assert str(error.value) == error_message


def test_invalid_content_id():
    """Test that initializing METS instance with invalid content_id raises
    ValueError.
    """
    with pytest.raises(ValueError) as error:
        METS(
            mets_profile=(
                "https://digitalpreservation.fi/mets-profiles/"
                "cultural-heritage"
            ),
            package_id="package_id",
            contract_id="contract_id",
            creator_name="Mr. Foo",
            content_id="ä"
        )
    assert str(error.value) == (
        "content_id 'ä' contains characters that are not printable US-ASCII "
        "characters"
    )


def test_invalid_record_status():
    """Test that initializing METS instance with invalid record_status raises
    ValueError.
    """
    with pytest.raises(ValueError) as error:
        METS(
            mets_profile=(
                "https://digitalpreservation.fi/mets-profiles/"
                "cultural-heritage"
            ),
            package_id="package_id",
            contract_id="contract_id",
            creator_name="Mr. Foo",
            record_status="invalid"
        )
    assert str(error.value) == (
        "'invalid' is not a valid value for record_status. Value must be one "
        "of ['submission', 'update', 'dissemination']"
    )


def test_no_specification_or_catalog_version():
    """Test that initializing METS instance with no specification or
    catalog_version raises ValueError.
    """
    with pytest.raises(ValueError) as error:
        METS(
            mets_profile=(
                "https://digitalpreservation.fi/mets-profiles/"
                "cultural-heritage"
            ),
            package_id="package_id",
            contract_id="contract_id",
            creator_name="Mr. Foo",
            catalog_version=None,
            specification=None
        )
    assert str(error.value) == (
        "Either catalog_version or specification has to be set"
    )


def test_add_agents():
    """Test that agents can be added to a METS object."""
    mets = METS(
        mets_profile=(
            "https://digitalpreservation.fi/mets-profiles/"
            "cultural-heritage"
        ),
        package_id="package_id",
        contract_id="contract_id",
        creator_name="Mr. Foo"
    )
    mets.add_agent(role="role", type="type", name="name")

    # Creator agent has been added on initialization, so there should be two
    # agents
    assert len(mets.agents) == 2

    # role and type should have been capitalized
    assert mets.agents[1].role == "ROLE"
    assert mets.agents[1].type == "TYPE"

    assert mets.agents[1].name == "name"


def test_serialization():
    """Test serializing METS object.

    More thorough testing should be done in serialize module tests.
    """
    mets = METS(
        mets_profile=(
            "https://digitalpreservation.fi/mets-profiles/"
            "cultural-heritage"
        ),
        package_id="package_id",
        contract_id="contract_id",
        creator_name="Mr. Foo"
    )

    result = mets.serialize()

    # bytes.index raises ValueError if subsection is not found
    result.index(b"package_id")
    result.index(b"contract_id")
    result.index(b"Mr. Foo")
