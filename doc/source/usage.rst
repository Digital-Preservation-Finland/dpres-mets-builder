Usage
=====
Creating a METS file with METS builder consists of following steps:

1. Create a METS object instance
2. Create digital objects and add metadata to them
3. Create a structural map and add the digital objects to it
4. Create/generate file references
5. Transform the METS object instance to a XML file

Create a METS object instance
-----------------------------

Initialize a METS object:

.. code-block:: python

    from mets_builder.mets import METS, MetsProfile, AgentRole, AgentType

    mets = METS(
        mets_profile=MetsProfile.CULTURAL_HERITAGE,
        contract_id="urn:uuid:abcd1234-abcd-1234-5678-abcd1234abcd",
        creator_name="CSC – IT Center for Science Ltd.",
        creator_type=AgentType.ORGANIZATION,
    )

Creator agent is already created in the object initialization, but additional agents can be added with the ``add_agent()`` function:

.. code-block:: python

    mets.add_agent(
        name="Melissa Mets",
        agent_role=AgentRole.ARCHIVIST,
        agent_type=AgentType.INDIVIDUAL
    )

Create digital objects and add metadata to them
-----------------------------------------------
For each digital object that should be included in the METS document, a ``DigitalObject`` instance should be created. Technical metadata that applies to the digital object can be added using metadata objects:

.. code-block:: python

    from pathlib import Path

    from mets_builder.digital_object import DigitalObject, DigitalObjectStream
    from mets_builder.metadata import ImportedMetadata, TechnicalImageMetadata

    picture = DigitalObject(
        path_in_sip="pictures/cat.jpeg"
    )

    md = TechnicalImageMetadata(
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

    picture.add_metadata(md)

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

If a digital object has streams, they can be added to the digital object using ``DigitalObjectStream`` class, and have individual metadata added to them:

.. code-block:: python

    movie = DigitalObject(
        path_in_sip="movies/cat_video.mkv"
    )
    audio_stream = DigitalObjectStream(metadata=[audio_md])
    video_stream = DigitalObjectStream(metadata=[video_md])
    movie.add_stream(audio_stream)
    movie.add_stream(video_stream)

Create a structural map and add the digital objects to it
---------------------------------------------------------
The digital objects should be given a structure with structural maps, using the ``StructuralMap`` class. Digital objects are grouped into divisions with ``StructuralMapDiv`` objects. Finally the structural maps are given to the ``METS`` object:

.. code-block:: python

    from mets_builder.structural_map import StructuralMap, StructuralMapDiv

    root_div = StructuralMapDiv(div_type="directory")
    pictures_div = StructuralMapDiv(div_type="image_files", digital_objects=[picture])
    movies_div = StructuralMapDiv(div_type="movie_files", digital_objects=[movie])
    root_div.add_divs([pictures_div, movies_div])

    structural_map = StructuralMap(root_div=root_div)

    mets.add_structural_map(structural_map)

Metadata that applies to all digital objects in a division can be added to the division:

.. code-block:: python

    descriptive_md = ImportedMetadata(
        data_path=Path("/home/mets-enthusiast/metadata/datacite.xml"),
        metadata_type="descriptive",
        metadata_format="DC",
        format_version="2.0"
    )

    root_div.add_metadata(descriptive_md)

Create/generate file references
-------------------------------
If there are no special needs for the file references, they can be simply generated from the digital objects added to the structural maps, placing all digital objects found in the structural maps into a single file group in file references:

.. code-block:: python

    mets.generate_file_references()

If the file references section needs a special structure, the file references can also be formed manually:

.. code-block:: python

    from mets_builder.file_references import FileReferences, FileGroup

    file_references = FileReferences()

    production_group = FileGroup(use="production", digital_objects=[movie])
    master_group = FileGroup(use="master", digital_objects=[picture])
    file_references.add_file_group(production_group)
    file_references.add_file_group(master_group)

    mets.add_file_references(file_references)

Transform the METS object instance to a XML file
------------------------------------------------
When the METS is fully formed, simply call ``to_xml()`` function to get an XML representation of the METS object instance, and write to a file:

.. code-block:: python

    with open("mets.xml", "wb") as f:
        f.write(mets.to_xml())
