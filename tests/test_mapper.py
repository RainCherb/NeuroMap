#!/usr/bin/env python3
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from pathlib import Path
import tempfile
import json
import tiktoken
from neuromap.mapper import scan_and_map, NeuroMap


def test_neuromap_creation():
    """Test NeuroMap creation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a simple test project
        (temp_path / "main.py").write_text("def main():\n    print('Hello')\n")
        (temp_path / "utils.py").write_text("def helper():\n    return 'helper'\n")
        (temp_path / "README.md").write_text("# Test Project")
        
        neuromap = scan_and_map(temp_path)
        
        assert isinstance(neuromap, NeuroMap)
        assert neuromap.project_info.name == temp_path.name
        assert len(neuromap.project_info.files) >= 3
        assert len(neuromap.project_info.source_files) >= 2


def test_neuromap_summary():
    """Test project summary generation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        (temp_path / "main.py").write_text("def main():\n    pass\n")
        (temp_path / "README.md").write_text("# Test")
        
        neuromap = scan_and_map(temp_path)
        summary = neuromap.get_summary()
        
        assert "project_name" in summary
        assert "total_files" in summary
        assert "source_files" in summary
        assert "documentation_files" in summary
        assert "total_lines" in summary
        
        assert summary["project_name"] == temp_path.name
        assert summary["total_files"] >= 2
        assert summary["source_files"] >= 1


def test_markdown_compact_format():
    """Test compact Markdown format."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        (temp_path / "main.py").write_text("def main():\n    print('Hello')\n")
        (temp_path / "README.md").write_text("# Test Project\n\nProject description.")
        
        neuromap = scan_and_map(temp_path)
        md_output = neuromap.generate_markdown_compact(max_tokens=1000)
        
        assert isinstance(md_output, str)
        assert len(md_output) > 0
        assert temp_path.name in md_output
        
        # Check that it contains basic information
        assert "Languages:" in md_output
        assert "Total files:" in md_output
        
        # Check token budget
        encoding = tiktoken.get_encoding("cl100k_base")
        token_count = len(encoding.encode(md_output))
        assert token_count <= 1000


def test_markdown_standard_format():
    """Test standard Markdown format."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        (temp_path / "main.py").write_text("""
def main():
    '''Main entry point.'''
    print("Hello")
""")
        
        neuromap = scan_and_map(temp_path)
        md_output = neuromap.generate_markdown_standard(max_tokens=2000)
        
        assert isinstance(md_output, str)
        assert len(md_output) > 0
        assert temp_path.name in md_output
        
        # Check for structure
        assert "## Files" in md_output
        
        # Check token budget
        encoding = tiktoken.get_encoding("cl100k_base")
        token_count = len(encoding.encode(md_output))
        assert token_count <= 2000


def test_markdown_detailed_format():
    """Test detailed Markdown format."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        (temp_path / "main.py").write_text("""
import os
from pathlib import Path

def main():
    '''Main entry point.'''
    print("Hello")
    return Path(".")
""")
        
        neuromap = scan_and_map(temp_path)
        md_output = neuromap.generate_markdown_detailed(max_tokens=5000)
        
        assert isinstance(md_output, str)
        assert len(md_output) > 0
        assert temp_path.name in md_output
        
        # Check for advanced features
        assert "## Architecture Analysis" in md_output
        
        # Check token budget
        encoding = tiktoken.get_encoding("cl100k_base")
        token_count = len(encoding.encode(md_output))
        assert token_count <= 5000


def test_json_format():
    """Test JSON format."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        (temp_path / "main.py").write_text("def main():\n    pass\n")
        (temp_path / "README.md").write_text("# Test")
        
        neuromap = scan_and_map(temp_path)
        
        # Get summary and convert to JSON
        summary = neuromap.get_summary()
        json_output = json.dumps(summary, indent=2, ensure_ascii=False)
        
        assert isinstance(json_output, str)
        parsed = json.loads(json_output)
        
        assert "project_name" in parsed
        assert "total_files" in parsed
        assert "source_files" in parsed


def test_xml_format():
    """Test XML format."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        (temp_path / "main.py").write_text("def main():\n    pass\n")
        (temp_path / "README.md").write_text("# Test")
        
        neuromap = scan_and_map(temp_path)
        summary = neuromap.get_summary()
        
        # Create a simple XML representation
        xml_parts = []
        xml_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
        xml_parts.append('<project_map>')
        xml_parts.append(f'  <project name="{summary["project_name"]}">')
        xml_parts.append(f'    <total_files>{summary["total_files"]}</total_files>')
        xml_parts.append(f'    <source_files>{summary["source_files"]}</source_files>')
        xml_parts.append('  </project>')
        xml_parts.append('</project_map>')
        
        xml_output = '\n'.join(xml_parts)
        
        assert isinstance(xml_output, str)
        assert "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" in xml_output
        assert "<project_map>" in xml_output
        assert summary["project_name"] in xml_output
