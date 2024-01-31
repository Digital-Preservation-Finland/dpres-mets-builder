Changelog
=========
All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Unreleased
----------
Added
^^^^^
- Class ``TechnicalAudioMetadata`` for creating technical audio metadata in AudioMD standard
- Class ``TechnicalVideoMetadata`` for creating technical video metadata in VideoMD standard
- Class ``TechnicalCSVMetadata`` for creating technical CSV metadata in ADDML standard
- Classes ``TechnicalFileObjectMetadata`` and ``TechnicalBitstreamObjectMetadata`` for representing file and bitstream technical metadata respectively using PREMIS objects
- Identical technical media metadata entries will automatically be deduplicated in the generated METS if possible
- Method ``StructuralMap.from_directory_structure`` to generate structural map from the directory structure of given digital objects

0.1.0 - 2023-06-14
------------------
Added
^^^^^
- RHEL9 compatible RPM spec file

0.0.1 - 2023-04-19
------------------
- First public release
