from __future__ import annotations

import json
from typing import Dict, Any, List
from pathlib import Path


def format_json(neuromap) -> str:
    """
    Generate a JSON formatted project map.
    """
    result = {
        "project": {
            "name": neuromap.project_info.name,
            "root": str(neuromap.project_info.root),
            "stats": {
                "total_files": neuromap.project_info.total_files,
                "total_lines": neuromap.project_info.total_lines,
                "directories": len(neuromap.project_info.directories),
                "language_stats": neuromap.project_info.language_stats,
            }
        },
        "source_files": [],
        "documentation_files": [],
        "config_files": [],
        "top_files": [],
        "entrypoints": neuromap.entrypoints,
        "symbols": [],
        "dependencies": [],
    }
    
    # Categorize files
    for file_info in neuromap.project_info.source_files:
        file_data = {
            "name": file_info.name,
            "path": str(file_info.path),
            "lines": file_info.lines,
            "size": file_info.size,
            "importance": get_file_importance(file_info),
        }
        
        if file_info.content:
            file_data["preview"] = file_info.content
            
        result["source_files"].append(file_data)
        
        # Add to top files list
        result["top_files"].append(file_data)
    
    # Add documentation files
    for file_info in neuromap.project_info.documentation_files:
        result["documentation_files"].append({
            "name": file_info.name,
            "path": str(file_info.path),
            "lines": file_info.lines,
            "size": file_info.size,
        })
    
    # Add config files
    for file_info in neuromap.project_info.files:
        if file_info.is_config:
            result["config_files"].append({
                "name": file_info.name,
                "path": str(file_info.path),
            })
    
    # Add symbols
    for sym in neuromap.symbols:
        result["symbols"].append({
            "name": sym.name,
            "file": sym.file,
            "type": sym.type,
            "lines": sym.lines,
            "docstring": sym.docstring,
            "imports": sym.imports,
            "calls": sym.calls,
            "confidence": sym.confidence,
        })
    
    # Add dependencies
    for dep in neuromap.dependencies:
        result["dependencies"].append({
            "source": dep.source,
            "target": dep.target,
            "type": dep.type,
            "confidence": dep.confidence,
        })
    
    # Sort top files by importance and lines
    result["top_files"].sort(key=lambda x: (x["importance"], x["lines"]), reverse=True)
    
    return json.dumps(result, indent=2, ensure_ascii=False)


from ..mapper import get_file_importance