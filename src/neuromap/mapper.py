from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import json
import tiktoken
from .scanner import scan_project, FileInfo, ProjectInfo
from .detectors.entrypoints import EntrypointDetector


@dataclass
class SymbolInfo:
    name: str
    file: str
    type: str  # "function", "class", "method", "import", "variable"
    lines: int
    docstring: Optional[str] = None
    imports: List[str] = field(default_factory=list)
    calls: List[str] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class DependencyInfo:
    source: str
    target: str
    type: str  # "imports", "calls", "extends", "implements"
    confidence: float = 1.0


@dataclass
class NeuroMap:
    project_info: ProjectInfo
    symbols: List[SymbolInfo] = field(default_factory=list)
    dependencies: List[DependencyInfo] = field(default_factory=list)
    entrypoints: List[Dict[str, Any]] = field(default_factory=list)
    patterns: Dict[str, Any] = field(default_factory=dict)

    def get_summary(self) -> Dict[str, Any]:
        """
        Generate a structured summary of the project.
        """
        return {
            "project_name": self.project_info.name,
            "total_files": self.project_info.total_files,
            "source_files": len(self.project_info.source_files),
            "documentation_files": len(self.project_info.documentation_files),
            "total_lines": self.project_info.total_lines,
            "main_languages": list(self.project_info.language_stats.keys()),
            "entrypoints_count": len(self.entrypoints),
            "symbols_count": len(self.symbols),
            "dependencies_count": len(self.dependencies),
            "top_symbols": [sym.name for sym in sorted(self.symbols, key=lambda x: x.confidence, reverse=True)[:10]],
            "architecture_patterns": self.patterns.get("architecture", []),
        }

    def generate_markdown_compact(self, max_tokens: int = 1000) -> str:
        """
        Generate a compact Markdown representation.
        """
        encoding = tiktoken.get_encoding("cl100k_base")
        parts = []
        token_count = 0
        
        # Header
        header = f"# {self.project_info.name}\n"
        parts.append(header)
        token_count += len(encoding.encode(header))
        
        # Basic project info
        info_lines = [
            f"\n**Languages:** {', '.join(self.project_info.language_stats.keys())}",
            f"**Total files:** {self.project_info.total_files}",
            f"**Code lines:** {self.project_info.total_lines}",
        ]
        
        for line in info_lines:
            if token_count + len(encoding.encode(line)) <= max_tokens - 300:
                parts.append(line)
                token_count += len(encoding.encode(line))
        
        # Entry points
        if self.entrypoints:
            parts.append("\n## Entry Points")
            for ep in self.entrypoints[:5]:
                ep_line = f"- `{ep['path']}`: {ep['description']}"
                if token_count + len(encoding.encode(ep_line)) <= max_tokens - 300:
                    parts.append(ep_line)
                    token_count += len(encoding.encode(ep_line))
        
        # Top symbols
        if self.symbols:
            parts.append("\n## Key Symbols")
            for sym in self.symbols[:10]:
                sym_line = f"- `{sym.name}` in {sym.file} ({sym.type})"
                if token_count + len(encoding.encode(sym_line)) <= max_tokens - 300:
                    parts.append(sym_line)
                    token_count += len(encoding.encode(sym_line))
        
        # Dependencies overview
        if self.dependencies:
            parts.append("\n## Dependencies")
            dep_summary = {}
            for dep in self.dependencies:
                if dep.type not in dep_summary:
                    dep_summary[dep.type] = set()
                dep_summary[dep.type].add(dep.target)
            
            for dep_type, targets in dep_summary.items():
                type_line = f"- **{dep_type}**: {', '.join(sorted(targets)[:5])}"
                if token_count + len(encoding.encode(type_line)) <= max_tokens - 300:
                    parts.append(type_line)
                    token_count += len(encoding.encode(type_line))
        
        return "\n".join(parts)

    def generate_markdown_standard(self, max_tokens: int = 2000) -> str:
        """
        Generate a standard Markdown representation.
        """
        encoding = tiktoken.get_encoding("cl100k_base")
        parts = []
        token_count = 0
        
        # Header with structure
        parts.append(f"# {self.project_info.name}")
        parts.append(f"\n**Paradigm:** {self.patterns.get('paradigm', 'Not defined')}")
        parts.append(f"**Architecture:** {', '.join(self.patterns.get('architecture', []))}")
        token_count += len(encoding.encode(f"# {self.project_info.name}\n"))
        
        # Detailed file information
        if self.project_info.source_files:
            parts.append("\n## Files")
            parts.append("```")
            parts.append(self._generate_tree_view())
            parts.append("```")
        
        # Entry points with details
        if self.entrypoints:
            parts.append("\n## Entry Points")
            for ep in self.entrypoints:
                ep_block = f"\n### {ep['path']}\n"
                ep_block += f"**Type:** {ep['type']}\n"
                ep_block += f"**Language:** {ep['language']}\n"
                ep_block += f"**Confidence:** {ep['confidence']:.1%}\n"
                ep_block += f"**Description:** {ep['description']}\n"
                ep_block += f"**Signature:** {ep['signature']}\n"
                
                if token_count + len(encoding.encode(ep_block)) <= max_tokens - 200:
                    parts.append(ep_block)
                    token_count += len(encoding.encode(ep_block))
        
        # Symbol index
        if self.symbols:
            parts.append("\n## Symbol Index")
            parts.append("\n| Symbol | File | Type | Confidence |")
            parts.append("|--------|------|------|------------|")
            
            for sym in sorted(self.symbols, key=lambda x: x.confidence, reverse=True)[:20]:
                sym_line = f"| {sym.name} | {sym.file} | {sym.type} | {sym.confidence:.1%} |"
                if token_count + len(encoding.encode(sym_line)) <= max_tokens - 200:
                    parts.append(sym_line)
                    token_count += len(encoding.encode(sym_line))
        
        # Dependency graph
        if self.dependencies:
            parts.append("\n## Dependencies")
            dep_groups = {}
            for dep in self.dependencies:
                if dep.type not in dep_groups:
                    dep_groups[dep.type] = []
                dep_groups[dep.type].append((dep.source, dep.target))
            
            parts.append("\n### Dependency Graph")
            parts.append("```mermaid")
            parts.append("graph TD")
            for dep_type, deps in dep_groups.items():
                parts.append(f"    %% {dep_type}")
                for source, target in deps[:10]:
                    parts.append(f"    {source} --> {target}")
            parts.append("```")
        
        return "\n".join(parts)

    def generate_markdown_detailed(self, max_tokens: int = 8000) -> str:
        """
        Generate a detailed Markdown representation.
        """
        encoding = tiktoken.get_encoding("cl100k_base")
        parts = []
        token_count = 0
        
        # Full project documentation
        parts.append(f"# Full Project Documentation: {self.project_info.name}")
        parts.append(f"\n**Size:** {self.project_info.total_files} files, {self.project_info.total_lines} lines of code")
        parts.append(f"**Languages:** {', '.join(self.project_info.language_stats.keys())}")
        
        # Architecture analysis
        if self.patterns:
            parts.append("\n## Architecture Analysis")
            if "architecture" in self.patterns:
                parts.append(f"**Architecture Patterns:** {', '.join(self.patterns['architecture'])}")
            if "paradigm" in self.patterns:
                parts.append(f"**Paradigm:** {self.patterns['paradigm']}")
            if "frameworks" in self.patterns:
                parts.append(f"**Frameworks:** {', '.join(self.patterns['frameworks'])}")
        
        # Complete file tree with annotations
        parts.append("\n## File Structure")
        parts.append("```")
        parts.append(self._generate_tree_view_detailed())
        parts.append("```")
        
        # All entry points
        if self.entrypoints:
            parts.append("\n## All Entry Points")
            for ep in self.entrypoints:
                ep_block = f"\n### {ep['path']}\n"
                ep_block += f"- **Type:** {ep['type']}\n"
                ep_block += f"- **Language:** {ep['language']}\n"
                ep_block += f"- **Confidence:** {ep['confidence']:.1%}\n"
                ep_block += f"- **Description:** {ep['description']}\n"
                ep_block += f"- **Signature:** {ep['signature']}\n"
                ep_block += f"- **References:** {', '.join(ep['references'][:3])}\n"
                
                if token_count + len(encoding.encode(ep_block)) <= max_tokens - 200:
                    parts.append(ep_block)
                    token_count += len(encoding.encode(ep_block))
        
        # Complete symbol index
        if self.symbols:
            parts.append("\n## Complete Symbol Index")
            parts.append("\n| Symbol | Type | File | Lines | Documentation |")
            parts.append("|--------|------|------|-------|---------------|")
            
            for sym in self.symbols:
                doc_preview = sym.docstring[:50] + "..." if sym.docstring and len(sym.docstring) > 50 else (sym.docstring or "")
                sym_line = f"| {sym.name} | {sym.type} | {sym.file} | {sym.lines} | {doc_preview} |"
                
                if token_count + len(encoding.encode(sym_line)) <= max_tokens - 200:
                    parts.append(sym_line)
                    token_count += len(encoding.encode(sym_line))
        
        # Complete dependency graph
        if self.dependencies:
            parts.append("\n## Complete Dependency Graph")
            dep_groups = {}
            for dep in self.dependencies:
                if dep.type not in dep_groups:
                    dep_groups[dep.type] = []
                dep_groups[dep.type].append((dep.source, dep.target))
            
            parts.append("\n### Dependency Visualization")
            parts.append("```mermaid")
            parts.append("graph TD")
            for dep_type, deps in dep_groups.items():
                parts.append(f"    classDef {dep_type} fill:#f0f0f0,stroke:#333,stroke-width:2px")
                for source, target in deps[:15]:
                    parts.append(f"    {source} --> {target}")
                    parts.append(f"    class {source} {dep_type}")
                    parts.append(f"    class {target} {dep_type}")
            parts.append("```")
            
            # Detailed dependency analysis
            parts.append("\n### Dependency Analysis")
            circular_deps = self._find_circular_dependencies()
            if circular_deps:
                parts.append(f"**Circular dependencies detected:** {len(circular_deps)}")
                for dep in circular_deps[:5]:
                    parts.append(f"- `{dep['source']}` -> `{dep['target']}`")
        
        return "\n".join(parts)

    def generate_claude(self, max_tokens: int = 2000) -> str:
        """
        Generate a CLAUDE.md project-context file for Claude Code.

        Claude Code automatically reads CLAUDE.md from the project root as
        background context. The layout below is tuned for that: it front-loads
        the essentials (tech stack, entry points, key files) that an assistant
        needs to orient itself, and keeps everything within the token budget.
        """
        encoding = tiktoken.get_encoding("cl100k_base")
        parts: List[str] = []
        token_count = 0

        def fits(text: str, reserve: int = 200) -> bool:
            nonlocal token_count
            return token_count + len(encoding.encode(text)) <= max_tokens - reserve

        def add(text: str, reserve: int = 200) -> None:
            nonlocal token_count
            if not fits(text, reserve):
                return
            parts.append(text)
            token_count += len(encoding.encode(text))

        # 1. Auto-generated banner so Claude doesn't rewrite it blindly.
        banner = (
            "<!-- Auto-generated by NeuroMap. Edit with care — "
            "re-running `neuromap scan --format claude` regenerates this file. -->"
        )
        add(banner, reserve=300)

        # 2. Header.
        add(f"\n# {self.project_info.name}", reserve=300)
        add(
            "\nProject context for Claude Code, distilled from the codebase. "
            "Use it to orient before editing.",
            reserve=300,
        )

        # 3. Tech stack: languages + detected frameworks.
        languages = list(self.project_info.language_stats.keys())
        frameworks = self.patterns.get("frameworks", [])
        add("\n## Tech Stack", reserve=300)
        if languages:
            add("**Languages:** " + ", ".join(languages), reserve=300)
        else:
            add("**Languages:** Not detected", reserve=300)
        if frameworks:
            add("**Frameworks:** " + ", ".join(frameworks), reserve=300)
        add(f"**Size:** {self.project_info.total_files} files, "
            f"{self.project_info.total_lines} lines of code", reserve=300)

        # 4. Project structure.
        add("\n## Project Structure", reserve=300)
        add("```", reserve=300)
        add(self._generate_tree_view(), reserve=300)
        add("```", reserve=300)

        # 5. Entry points — the most important orientation info.
        if self.entrypoints:
            add("\n## Entry Points", reserve=300)
            for ep in self.entrypoints[:10]:
                line = f"- `{ep['path']}` — {ep['type']}: {ep['description']}"
                add(line, reserve=300)

        # 6. Key files & symbols.
        add("\n## Key Files & Symbols", reserve=300)
        important_files = sorted(
            self.project_info.source_files,
            key=get_file_importance,
            reverse=True,
        )[:10]
        for file_info in important_files:
            line = f"- `{file_info.name}` ({file_info.lines} lines)"
            add(line, reserve=300)

        if self.symbols:
            add("\n### Top Symbols", reserve=300)
            for sym in sorted(self.symbols, key=lambda x: x.confidence, reverse=True)[:15]:
                line = f"- `{sym.name}` ({sym.type}) in {sym.file}"
                add(line, reserve=300)

        # 7. Architecture.
        arch_patterns = self.patterns.get("architecture", [])
        paradigm = self.patterns.get("paradigm")
        if arch_patterns or paradigm:
            add("\n## Architecture", reserve=300)
            if arch_patterns:
                add(f"**Patterns:** {', '.join(arch_patterns)}", reserve=300)
            if paradigm and paradigm != "Not defined":
                add(f"**Paradigm:** {paradigm}", reserve=300)

        # 8. Dependencies overview (grouped, like the compact format).
        if self.dependencies:
            add("\n## Dependencies", reserve=300)
            dep_summary: Dict[str, set] = {}
            for dep in self.dependencies:
                dep_summary.setdefault(dep.type, set()).add(dep.target)
            for dep_type, targets in dep_summary.items():
                line = f"- **{dep_type}**: {', '.join(sorted(targets)[:5])}"
                add(line, reserve=300)

        # 9. Footer.
        add(
            "\n---\n_Regenerated by `neuromap scan <path> --format claude`._",
            reserve=100,
        )

        return "\n".join(parts)

    def _generate_tree_view(self) -> str:
        """
        Generate a tree view of the project structure.
        """
        lines = []
        
        # Add root
        lines.append(f"{self.project_info.name}/")
        
        # Group files by importance
        important_files = []
        other_files = []
        
        for file_info in self.project_info.source_files:
            importance = get_file_importance(file_info)
            if importance > 0.7:
                important_files.append(file_info)
            else:
                other_files.append(file_info)
        
        # Add important files
        for file_info in important_files:
            lines.append(f"  └── ★ {file_info.name} ({file_info.lines} lines)")
        
        # Add other files
        for file_info in other_files[:5]:
            lines.append(f"  └── {file_info.name} ({file_info.lines} lines)")
        
        # Add directories
        if self.project_info.directories:
            lines.append("  📁 ... (other directories)")
        
        return "\n".join(lines)

    def _generate_tree_view_detailed(self) -> str:
        """
        Generate a detailed tree view with annotations.
        """
        lines = []
        
        # Add root with metadata
        lines.append(f"{self.project_info.name}/")
        lines.append(f"  📝 pyproject.toml  — Project Configuration")
        lines.append(f"  📚 README.md  — Project Documentation")
        
        # Add important directories
        if "src" in self.project_info.directories:
            lines.append(f"  📁 src/  — Source Code")
            lines.append(f"    ├── main.py  — Entry Point")
            lines.append(f"    ├── api/  — API Interface")
            lines.append(f"    ├── models/  — Data Models")
            lines.append(f"    └── utils/  — Utility Functions")
        
        if "tests" in self.project_info.directories:
            lines.append(f"  📁 tests/  — Tests")
            lines.append(f"    └── test_main.py  — Core Functionality Tests")
        
        # Add remaining directories
        for directory in self.project_info.directories:
            if directory not in ["src", "tests"]:
                lines.append(f"  📁 {directory}/")
        
        # Add remaining source files
        important_files = sorted(
            self.project_info.source_files, 
            key=lambda x: get_file_importance(x), 
            reverse=True
        )
        
        for file_info in important_files[:10]:
            importance = get_file_importance(file_info)
            marker = " ★" if importance > 0.7 else ""
            lines.append(f"  └──{marker} {file_info.name} ({file_info.lines} lines)")
        
        return "\n".join(lines)

    def _find_circular_dependencies(self) -> List[Dict[str, str]]:
        """
        Find circular dependencies in the graph.
        """
        # Placeholder implementation
        return []


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


def scan_and_map(
    path: Path,
    level: str = "compact",
    max_depth: int = -1,
) -> NeuroMap:
    """
    Scan a project and generate a NeuroMap.
    """
    # Step 1: Scan file system
    project_info = scan_project(path, max_depth=max_depth)
    
    # Step 2: Detect entry points
    entrypoint_detector = EntrypointDetector()
    entrypoint_files = [f.path for f in project_info.source_files if f.content]
    entrypoints = entrypoint_detector.detect_entrypoints(entrypoint_files)
    
    # Step 3: Extract symbols (placeholder for tree-sitter integration)
    symbols = []
    # TODO: Integrate with tree-sitter for symbol extraction
    
    # Step 4: Build dependency graph (placeholder)
    dependencies = []
    # TODO: Parse import/call statements from source files
    
    # Step 5: Detect patterns
    patterns = detect_patterns(project_info, symbols)
    
    return NeuroMap(
        project_info=project_info,
        symbols=symbols,
        dependencies=dependencies,
        entrypoints=[ep.to_dict() for ep in entrypoints],
        patterns=patterns,
    )


def detect_patterns(project_info: ProjectInfo, symbols: List[SymbolInfo]) -> Dict[str, Any]:
    """
    Detect architectural patterns and project characteristics.
    """
    patterns = {
        "architecture": [],
        "paradigm": "Not defined",
        "frameworks": [],
        "databases": [],
    }
    
    # Detect architecture patterns
    if "src" in project_info.directories:
        if "api" in project_info.directories and "models" in project_info.directories:
            patterns["architecture"].append("MVC")
    
    if "src" in project_info.directories and "tests" in project_info.directories:
        patterns["architecture"].append("Test stack")
    
    # Detect frameworks from files
    for file_info in project_info.files:
        name_lower = file_info.name.lower()
        content = file_info.content or ""
        if "fastapi" in name_lower or any(x in content for x in ["FastAPI", "fastapi"]):
            patterns["frameworks"].append("FastAPI")
        elif "django" in name_lower or any(x in content for x in ["Django", "django"]):
            patterns["frameworks"].append("Django")
        elif "spring" in name_lower or "pom.xml" in name_lower:
            patterns["frameworks"].append("Spring")
    
    return patterns