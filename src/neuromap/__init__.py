from __future__ import annotations

__version__ = "0.1.0"
__all__ = ["__version__"]

from .cli import app
from .scanner import scan_project, FileInfo, ProjectInfo
from .mapper import scan_and_map, NeuroMap

__all__.extend(["app", "scan_project", "FileInfo", "ProjectInfo", "scan_and_map", "NeuroMap"])