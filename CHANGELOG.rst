Changelog
=========
All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Unreleased
----------
Added
^^^^^
- Automatically add PREMIS agent to structural map div metadata, if an event to which the agent is linked is added.

Changed
^^^^^^^
- Rename MetadataBase class to Metadata
- Make Metadata an abstract base class
- Rename ``DigitalObject`` attribute ``sip_filepath`` to ``path``

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
