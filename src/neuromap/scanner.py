from __future__ import annotations

import os
import fnmatch
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class FileInfo:
    path: Path
    name: str
    extension: str
    size: int
    lines: int
    content: str | None = None
    is_hidden: bool = False
    is_symlink: bool = False

    @property
    def is_source_file(self) -> bool:
        source_extensions = {
            '.py', '.js', '.ts', '.tsx', '.jsx', '.java', 
            '.cpp', '.cc', '.cxx', '.c', '.h', '.hpp',
            '.rs', '.go', '.php', '.rb', '.swift', '.kt'
        }
        return self.extension.lower() in source_extensions

    @property
    def is_documentation(self) -> bool:
        doc_extensions = {'.md', '.rst', '.txt'}
        return self.extension.lower() in doc_extensions

    @property
    def is_config(self) -> bool:
        config_names = {'config', 'settings', 'setup', 'pyproject', 'package'}
        return any(name.lower() in config_names for name in self.name.lower().split('.'))


@dataclass
class ProjectInfo:
    root: Path
    name: str
    files: List[FileInfo] = field(default_factory=list)
    directories: List[str] = field(default_factory=list)
    language_stats: Dict[str, int] = field(default_factory=dict)
    total_lines: int = 0
    total_files: int = 0

    def add_file(self, file_info: FileInfo):
        self.files.append(file_info)
        self.total_files += 1
        self.total_lines += file_info.lines

    @property
    def source_files(self) -> List[FileInfo]:
        return [f for f in self.files if f.is_source_file]

    @property
    def documentation_files(self) -> List[FileInfo]:
        return [f for f in self.files if f.is_documentation]


def scan_project(root_path: Path, max_depth: int = -1) -> ProjectInfo:
    """
    Scan a project directory and return structured information.
    """
    project = ProjectInfo(
        root=root_path,
        name=root_path.name or "Project"
    )
    
    _walk_directory(root_path, project, current_depth=0, max_depth=max_depth)
    
    return project


def _walk_directory(
    current_path: Path, 
    project: ProjectInfo, 
    current_depth: int,
    max_depth: int
):
    """
    Recursively walk a directory and collect file information.
    """
    if max_depth >= 0 and current_depth > max_depth:
        return
    
    try:
        for entry in current_path.iterdir():
            if entry.name.startswith('.'):
                continue
                
            if entry.is_file():
                file_info = _analyze_file(entry)
                project.add_file(file_info)
            elif entry.is_dir():
                project.directories.append(entry.name)
                _walk_directory(entry, project, current_depth + 1, max_depth)
    except (PermissionError, OSError):
        pass


def _analyze_file(file_path: Path) -> FileInfo:
    """
    Analyze a single file and extract metadata.
    """
    try:
        stat = file_path.stat()
        name = file_path.name
        extension = file_path.suffix
        size = stat.st_size
        lines = 0
        content = None
        
        # Count lines for source files
        if file_path.suffix.lower() in {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', 
                                       '.cpp', '.cc', '.cxx', '.c', '.h', '.hpp', 
                                       '.rs', '.go', '.php', '.rb', '.swift', '.kt'}:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    lines += 1
                
                # Store first 3 lines as preview for source files
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    preview_lines = []
                    for i, line in enumerate(f):
                        if i < 3:
                            preview_lines.append(line.rstrip())
                        else:
                            break
                    content = '\n'.join(preview_lines)
        
        return FileInfo(
            path=file_path,
            name=name,
            extension=extension,
            size=size,
            lines=lines,
            content=content
        )
    except (OSError, UnicodeDecodeError):
        return FileInfo(
            path=file_path,
            name=file_path.name,
            extension=file_path.suffix,
            size=0,
            lines=0,
            content=None
        )