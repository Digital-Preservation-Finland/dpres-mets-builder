Usage
=====
Creating a METS document with METS builder consists of the following steps:

1. Create a METS object instance
2. Create digital objects and add metadata to them
3. Create/generate a structural map organizing the digital objects to a wanted structure
4. Create/generate file references
5. Transform the METS object instance to an XML file

The example code here can be found in full at the :doc:`example_code` section.

Create a METS object instance
-----------------------------

Initialize a METS object:

.. code-block:: python

    from mets_builder import METS, MetsProfile, AgentRole, AgentType

    mets = METS(
        mets_profile=MetsProfile.CULTURAL_HERITAGE,
        contract_id="urn:uuid:abcd1234-abcd-1234-5678-abcd1234abcd",
        creator_name="CSC – IT Center for Science Ltd.",
        creator_type=AgentType.ORGANIZATION,
    )

The obligatory creator agent is already created in the object initialization, but additional agents can be added with the ``add_agent()`` method:

.. code-block:: python

    mets.add_agent(
        name="Melissa Mets",
        agent_role=AgentRole.ARCHIVIST,
        agent_type=AgentType.INDIVIDUAL
    )

Create digital objects and add metadata to them
-----------------------------------------------
A ``DigitalObject`` instance should be created for each digital object that should be included in the METS document. Technical metadata that applies to the digital object can be added using metadata objects:

.. code-block:: python

    from pathlib import Path

    from mets_builder import DigitalObject, DigitalObjectStream
    from mets_builder.metadata import (
        ImportedMetadata, TechnicalBitstreamObjectMetadata,
        TechnicalImageMetadata, TechnicalFileObjectMetadata
    )

    picture = DigitalObject(
        path="data/pictures/cat_picture.jpg"
    )

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

Metadata that has been prepared earlier can be imported using the ``ImportedMetadata`` class:

.. code-block:: python

    audio_md = ImportedMetadata(
        data_path=Path("/home/mets-enthusiast/metadata/audiomd.xml"),
        metadata_type="technical",
        metadata_format="OTHER",
        other_format="AudioMD",
        format_version="2.0"
    )

    video_md = ImportedMetadata(
        data_path=Path("/home/mets-enthusiast/metadata/videomd.xml"),
        metadata_type="technical",
        metadata_format="OTHER",
        other_format="VideoMD",
        format_version="2.0"
    )

If a digital object has streams (for example video files often consist of video and audio streams in a container), the streams can be added to the digital object using ``DigitalObjectStream`` class, and have metadata of their own added to them:

.. code-block:: python

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

Create/generate a structural map organizing the digital objects to a wanted structure
-------------------------------------------------------------------------------------
The digital objects should be given a structure with structural maps, using the ``StructuralMap`` class. Digital objects are grouped into divisions with ``StructuralMapDiv`` objects. Finally the structural maps are given to the ``METS`` object.

A structural map can be generated according to the directory structure inferred from the ``path`` attributes of the given ``DigitalObject`` instances, turning each directory found in the filepaths to a division in the structural map, finally placing the digital objects in the correct division:

.. code-block:: python

    from mets_builder import StructuralMap, StructuralMapDiv

    structural_map = StructuralMap.from_directory_structure([picture, movie])
    mets.add_structural_map(structural_map)

However, it is possible to build the structural map manually if different structure for the files is needed:

.. code-block:: python

    root_div = StructuralMapDiv(div_type="directory")
    pictures_div = StructuralMapDiv(div_type="image_files", digital_objects=[picture])
    movies_div = StructuralMapDiv(div_type="movie_files", digital_objects=[movie])
    root_div.add_divs([pictures_div, movies_div])

    structural_map = StructuralMap(root_div=root_div)
    mets.add_structural_map(structural_map)


Metadata that applies to all digital objects in a division can be added to the division. For example digital provenance event information could describe all digital files, so that could be written to the root div of the structural map:

.. code-block:: python

    event_md = DigitalProvenanceEventMetadata(
        event_type="message digest calculation",
        event_datetime="2000-01-01T12:00:00",
        detail="Checksum calculation for digital objects",
        outcome="success",
        outcome_detail=(
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

Create/generate file references
-------------------------------
If there are no special needs for the file references, they can be generated from the digital objects added to the structural maps, placing all digital objects found in the structural maps into a single file group in file references:

.. code-block:: python

    mets.generate_file_references()

If the file references section needs a special structure, the file references can also be formed manually:

.. code-block:: python

    from mets_builder import FileReferences, FileGroup

    file_references = FileReferences()

    production_group = FileGroup(use="production", digital_objects=[movie])
    master_group = FileGroup(use="master", digital_objects=[picture])
    file_references.add_file_group(production_group)
    file_references.add_file_group(master_group)

    mets.add_file_references(file_references)

Transform the METS object instance to an XML file
-------------------------------------------------
When the METS is fully formed, the ``write`` method of the METS object can be called to write an XML representation of the METS object to the given file path:

.. code-block:: python

    mets.write("/home/mets-enthusiast/mets.xml")
