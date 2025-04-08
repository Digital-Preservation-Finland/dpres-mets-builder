Changelog
=========
All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

..
    Ensure next release is 2.0.0!
Unreleased
----------
Removed
^^^^^^^
- ``Metadata.add_metadata`` no longer automatically adds all linked metadata objects; only linked agents are added now.

1.1.1 - 2025-04-02
------------------
Fixed
^^^^^
- Fix normalization and conversion events getting incorrectly bundled when using ``StructuralMapDiv.bundle_metadata``

1.1.0 - 2025-02-26
------------------
Changed
^^^^^^^
- Update to meet specifications version 1.7.7
- Set default version of Datacite metadata to 4.3


1.0.0 - 2024-09-09
------------------
Added
^^^^^
- Add linked metadata to structural maps and digital objects automatically
- Add ``bundle_metadata`` method to ``StructuralMapDiv`` which will move shared metadata entries to the structural map div from child digital objects and structural map divs recursively.
- Add ``ImportedMetadata.from_path`` and ``ImportedMetadata.from_string`` to automatically detect external XML metadata and create a corresponding ``ImportedMetadata`` instance.

Changed
^^^^^^^
- Rename MetadataBase class to Metadata
- Make Metadata an abstract base class
- Rename various class attributes
  - ``DigitalObject``
    - ``sip_filepath`` to ``path``
  - ``DigitalProvenanceAgentMetadata``
    - ``agent_note`` to ``note``
    - ``agent_version`` to ``version``
    - ``agent_name`` to ``name``
  - ``DigitalProvenanceEventMetadata``
    - ``event_datetime`` to ``datetime``
    - ``event_outcome`` to ``outcome``
    - ``event_outcome_detail`` to ``outcome_detail``
    - ``event_detail`` to ``detail``
- Make several functions take an iterable as an argument instead of a single object. Rename functions to reflect this.
  - ``DigitalObject.add_metadata`` and ``StructuralMapDiv.add_metadata`` methods take an iterable containing metadata objects as an argument instead of a single metadata object
  - ``DigitalObject.add_stream`` to ``DigitalObject.add_streams``
  - ``FileGroup.add_digital_object`` to ``FileGroup.add_digital_objects``
  - ``FileReferences.add_file_group`` to ``FileReferences.add_file_groups``
  - ``METS.add_structural_map`` to ``METS.add_structural_maps``

Removed
^^^^^^^
- Creation of automatic PREMIS events when adding imported metadata to structural map. This functionality is moved over to ``siptool-ng``.
- ``from_directory_structure`` method from ``StructureMap`` class. This functionality is moved over to ``siptool-ng``.

0.3.0 - 2024-03-27
------------------
Added
^^^^^
- Identical digital provenance event metadata entries will automatically be deduplicated in the generated METS if possible

Changed
^^^^^^^
- Pre-generated events and agents use UUIDs instead of hardcoded identifiers


0.2.0 - 2024-02-29
------------------
Added
^^^^^
- Class ``TechnicalAudioMetadata`` for creating technical audio metadata in AudioMD standard
- Class ``TechnicalVideoMetadata`` for creating technical video metadata in VideoMD standard
- Class ``TechnicalCSVMetadata`` for creating technical CSV metadata in ADDML standard
- Classes ``TechnicalFileObjectMetadata`` and ``TechnicalBitstreamObjectMetadata`` for representing file and bitstream technical metadata respectively using PREMIS objects
- Identical technical media metadata entries will automatically be deduplicated in the generated METS if possible
- Method ``StructuralMap.from_directory_structure`` to generate structural map from the directory structure of given digital objects
- Method ``DigitalProvenanceAgentMetadata.get_mets_builder_agent`` for creating agent metadata for ``dpres-mets-builder``

Fixed
^^^^^
- Removed empty DMDID attributes from structMap divs in the serialized METS

Changed
^^^^^^^
- ``NAMESPACES`` constant in ``serialize`` module was made public
- Updated to meet specifications version 1.7.6

0.1.0 - 2023-06-14
------------------
Added
^^^^^
- RHEL9 compatible RPM spec file

0.0.1 - 2023-04-19
------------------
- First public release
