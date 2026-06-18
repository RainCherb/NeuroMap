from __future__ import annotations

from typing import Dict, Any, List
from pathlib import Path


def format_xml(project_info) -> str:
    """
    Generate an XML formatted project map.
    """
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<project_map>')
    
    # Project info
    lines.append(f'  <project name="{project_info.name}" root="{project_info.root}">')
    lines.append(f'    <stats>')
    lines.append(f'      <total_files>{project_info.total_files}</total_files>')
    lines.append(f'      <total_lines>{project_info.total_lines}</total_lines>')
    lines.append(f'      <directories>{len(project_info.directories)}</directories>')
    
    if project_info.language_stats:
        lines.append(f'      <languages>')
        for lang, count in project_info.language_stats.items():
            lines.append(f'        <language name="{lang}">{count}</language>')
        lines.append(f'      </languages>')
    
    lines.append(f'    </stats>')
    
    # Source files
    lines.append(f'    <source_files>')
    for file_info in project_info.source_files:
        importance = get_file_importance(file_info)
        lines.append(f'      <file name="{file_info.name}" path="{file_info.path}">')
        lines.append(f'        <lines>{file_info.lines}</lines>')
        lines.append(f'        <size>{file_info.size}</size>')
        lines.append(f'        <importance>{importance}</importance>')
        if file_info.content:
            lines.append(f'        <preview><![CDATA[{file_info.content}]]></preview>')
        lines.append(f'      </file>')
    lines.append(f'    </source_files>')
    
    # Documentation files
    lines.append(f'    <documentation_files>')
    for file_info in project_info.documentation_files:
        lines.append(f'      <file name="{file_info.name}" path="{file_info.path}">')
        lines.append(f'        <lines>{file_info.lines}</lines>')
        lines.append(f'        <size>{file_info.size}</size>')
        lines.append(f'      </file>')
    lines.append(f'    </documentation_files>')
    
    lines.append(f'  </project>')
    lines.append('</project_map>')
    
    return '\n'.join(lines)


from ..mapper import get_file_importance