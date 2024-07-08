"""Example code to demonstrate how to use dpres-mets-builder."""
from pathlib import Path

from mets_builder import (METS, AgentRole, AgentType, DigitalObject,
                          DigitalObjectStream, FileGroup, FileReferences,
                          MetsProfile, StructuralMap, StructuralMapDiv)
from mets_builder.metadata import (DigitalProvenanceAgentMetadata,
                                   DigitalProvenanceEventMetadata,
                                   ImportedMetadata,
                                   TechnicalBitstreamObjectMetadata,
                                   TechnicalFileObjectMetadata,
                                   TechnicalImageMetadata)

# Initialize METS object with the package information
mets = METS(
    mets_profile=MetsProfile.CULTURAL_HERITAGE,
    contract_id="urn:uuid:abcd1234-abcd-1234-5678-abcd1234abcd",
    creator_name="CSC – IT Center for Science Ltd.",
    creator_type=AgentType.ORGANIZATION,
)

# Additional agents can be added to the METS object
mets.add_agent(
    name="Melissa Mets",
    agent_role=AgentRole.ARCHIVIST,
    agent_type=AgentType.INDIVIDUAL
)

# DigitalObject should be created for each digital object included in the METS
picture = DigitalObject(
    path="data/pictures/cat_picture.jpg"
)

# Metadata can be added to digital objects using calsses from metadata module
object_md = TechnicalFileObjectMetadata(
    file_format="image/jpeg",
    file_format_version="1.01",
    checksum_algorithm="MD5",
    checksum="4b05bb123f3a00187d3b1b130d67af1c",
    file_created_date="2000-12-24T22:00:00"
)

image_md = TechnicalImageMetadata(
    compression="jpeg",
    colorspace="rgb",
    width="100",
    height="200",
    bps_value="8",
    bps_unit="integer",
    samples_per_pixel="3",
    mimetype="image/jpeg",
    byte_order="little endian"
)

picture.add_metadata(object_md)
picture.add_metadata(image_md)

# Already existing metadata can be imported with ImportedMetadata class
audio_md = ImportedMetadata(
    data_path=Path("data/audio_metadata.xml"),
    metadata_type="technical",
    metadata_format="OTHER",
    other_format="AudioMD",
    format_version="2.0"
)

video_md = ImportedMetadata(
    data_path=Path("data/video_metadata.xml"),
    metadata_type="technical",
    metadata_format="OTHER",
    other_format="VideoMD",
    format_version="2.0"
)

# Streams within file (such as audio and video streams in video file) can be
# declared with DigitalObjectStream class, and the streams can be documented
# with metadata of their own
container_md = TechnicalFileObjectMetadata(
    file_format="video/x-matroska",
    file_format_version="4",
    checksum_algorithm="MD5",
    checksum="686b680720c61512f5fb438f7879aa76",
    file_created_date="2000-12-24T22:00:00"
)
movie = DigitalObject(
    path="data/movies/cat_video.mkv",
    metadata=[container_md]
)
audio_bitstream_md = TechnicalBitstreamObjectMetadata(
    file_format="audio/flac",
    file_format_version="1.2.1"
)
video_bitstream_md = TechnicalBitstreamObjectMetadata(
    file_format="video/x-ffv",
    file_format_version="3"
)
audio_stream = DigitalObjectStream(metadata=[audio_bitstream_md, audio_md])
video_stream = DigitalObjectStream(metadata=[video_bitstream_md, video_md])
movie.add_stream(audio_stream)
movie.add_stream(video_stream)

# Structure of the digital objects can be documented with the StructuralMap
# class, dividing the digital objects to wanted groups with StructuralMapDiv
# objects.
#
# Structural map can be generated according to the directory structure as
# inferred from the 'path' attributes of the DigitalObjects.  Here 'picture'
# and 'movie' has their 'path' defined as 'data/pictures/cat_picture.jpg' and
# 'data/movies/cat_video.mkv', so the method will create StructuralMapDivs with
# types 'data', 'movies' and 'pictures', and put the picture file to the
# 'pictures' div and video file to the 'movies' div. The whole structure will
# also be put inside a root div with type 'directory'.
structural_map = StructuralMap.from_directory_structure([picture, movie])
mets.add_structural_map(structural_map)

# If a special structure is needed, it can also be created manually.
#
# There can be multiple structural maps, so this will be added alongside the
# previously added structural map
root_div = StructuralMapDiv(div_type="directory")
pictures_div = StructuralMapDiv(
    div_type="image_files",
    digital_objects=[picture]
)
movies_div = StructuralMapDiv(
    div_type="movie_files",
    digital_objects=[movie]
)
root_div.add_divs([pictures_div, movies_div])

structural_map = StructuralMap(root_div=root_div)
mets.add_structural_map(structural_map)

# When metadata applies to all digital objects found in a division, the
# metadata can be applied to the division. For example digital provenance
# event information could describe all digital files, so that could be written
# to the root div of the structural map
event_md = DigitalProvenanceEventMetadata(
    event_type="message digest calculation",
    event_datetime="2000-01-01T12:00:00",
    event_detail="Checksum calculation for digital objects",
    event_outcome="success",
    event_outcome_detail=(
        "Checksum(s) successfully calculated for digital object(s)."
    )
)
agent_md = DigitalProvenanceAgentMetadata(
    agent_name="checksum-calculator",
    agent_type="software",
    agent_version="1.2.4"
)
event_md.link_agent_metadata(
    agent_metadata=agent_md,
    agent_role="executing program"
)
root_div.add_metadata(event_md)
root_div.add_metadata(agent_md)

# File references can be generated with the following command
mets.generate_file_references()

# If special structure for the file references is needed, the file references
# can be formed manually. There can be only one file references section, so
# this will overwrite the file references generated with the previous command
file_references = FileReferences()

picture_group = FileGroup(use="picture", digital_objects=[picture])
video_group = FileGroup(use="video", digital_objects=[movie])
file_references.add_file_group(picture_group)
file_references.add_file_group(video_group)

mets.add_file_references(file_references)

# When ready, the METS object can be serialized as XML-formatted METS document
# to the chosen filepath
mets.write("mets.xml")
