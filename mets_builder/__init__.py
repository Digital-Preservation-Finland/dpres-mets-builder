"""Default imports for mets_builder"""
from mets_builder.digital_object import DigitalObject, DigitalObjectStream
from mets_builder.file_references import FileGroup, FileReferences
from mets_builder.mets import (METS, AgentRole, AgentType, MetsProfile,
                               MetsRecordStatus)
from mets_builder.structural_map import StructuralMap, StructuralMapDiv

try:
    from ._version import version as __version__
except ImportError:
    # Package not installed, provide something
    __version__ = "N/A"

__all__ = [
    "DigitalObject", "DigitalObjectStream", "FileGroup", "FileReferences",
    "METS", "AgentRole", "AgentType", "MetsProfile", "MetsRecordStatus",
    "StructuralMap", "StructuralMapDiv"
]
