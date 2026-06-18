from __future__ import annotations

from typing import Dict, Any, List
from pathlib import Path
import tiktoken
from ..mapper import get_file_importance


def format_markdown(neuromap, max_tokens: int = 1000) -> str:
    """
    Generate a Markdown formatted project map.
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    lines = []
    current_tokens = 0
    
    # Header
    header = f"# {neuromap.project_info.name}"
    lines.append(header)
    current_tokens += len(encoding.encode(header))
    
    # Basic info from summary
    summary = neuromap.get_summary()
    info_lines = [
        f"\n**Languages:** {', '.join(neuromap.project_info.language_stats.keys()) if neuromap.project_info.language_stats else 'Not defined'}",
        f"**Total files:** {neuromap.project_info.total_files}",
        f"**Total lines of code:** {neuromap.project_info.total_lines}",
        f"**Directories:** {len(neuromap.project_info.directories)}",
    ]
    
    for line in info_lines:
        if current_tokens + len(encoding.encode(line)) > max_tokens - 200:
            break
        lines.append(line)
        current_tokens += len(encoding.encode(line))
    
    # Entry points
    if neuromap.entrypoints:
        lines.append("\n## Entry Points")
        for ep in neuromap.entrypoints[:5]:
            ep_line = f"- `{ep['path']}`: {ep['description']}"
            if current_tokens + len(encoding.encode(ep_line)) <= max_tokens - 300:
                lines.append(ep_line)
                current_tokens += len(encoding.encode(ep_line))
    
    # Top symbols
    if neuromap.symbols:
        lines.append("\n## Key Symbols")
        for sym in neuromap.symbols[:10]:
            sym_line = f"- `{sym.name}` in {sym.file} ({sym.type})"
            if current_tokens + len(encoding.encode(sym_line)) <= max_tokens - 300:
                lines.append(sym_line)
                current_tokens += len(encoding.encode(sym_line))
    
    return "\n".join(lines)


def get_file_importance(file_info) -> float:
    """
    Calculate importance score for a file (0.0 to 1.0).
    """
    score = 0.0
    
    if file_info.name in ['main.py', 'index.js', 'app.py', 'main.js', 'App.kt']:
        score += 0.4
    
    if file_info.is_source_file:
        score += 0.3
    
    if file_info.lines > 100:
        score += 0.2
    
    if file_info.name in ['README.md', 'pyproject.toml', 'package.json', 'Dockerfile']:
        score += 0.1
    
    return min(score, 1.0)