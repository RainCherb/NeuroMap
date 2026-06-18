from __future__ import annotations

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class EntrypointInfo:
    path: Path
    type: str  # "main", "api", "cli", "worker"
    language: str
    confidence: float
    signature: str
    description: str
    references: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": str(self.path),
            "type": self.type,
            "language": self.language,
            "confidence": self.confidence,
            "signature": self.signature,
            "description": self.description,
            "references": self.references,
        }


class EntrypointDetector:
    """
    Detect entry points in a project.
    """
    
    MAIN_PATTERNS = [
        r'def\s+main\s*\(\s*\)\s*:',
        r'if\s+__name__\s*==\s*["\']__main__["\']\s*:',
        r'def\s+main\s*\([^)]*\)\s*:',
    ]
    
    API_PATTERNS = [
        r'@app\.route\s*\(',
        r'@router\.\w+\s*\(',
        r'@fastapi\.APIRoute\s*\(',
        r'@flask\.route\s*\(',
        r'@django\.path\s*\(',
        r'class.*Flask.*App\s*:',
        r'class.*FastAPI\s*:',
        r'class.*DRF\w*Resource\s*:',
    ]
    
    CLI_PATTERNS = [
        r'typer\.\w+\s*\(',
        r'click\.\w+\s*\(',
        r'@.*app\.command\s*\(',
        r'@.*cli\.\w+\s*\(',
    ]
    
    WORKER_PATTERNS = [
        r'def\s+(?:worker|consumer|listener)\s*\(',
        r'@.*\.signal\s*\(',
        r'@.*\.task\s*\(',
    ]
    
    def __init__(self):
        self.entrypoints: List[EntrypointInfo] = []
    
    def detect_entrypoints(self, source_files: List[str]) -> List[EntrypointInfo]:
        """
        Detect entry points from source files.
        """
        self.entrypoints.clear()
        
        for file_path in source_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Detect entry points based on patterns
                if self._detect_main(content):
                    self.entrypoints.append(
                        EntrypointInfo(
                            path=Path(file_path),
                            type="main",
                            language=self._detect_language(file_path),
                            confidence=self._calculate_confidence(content, self.MAIN_PATTERNS),
                            signature=self._extract_signature(content),
                            description=self._describe_entrypoint("main"),
                        )
                    )
                
                if self._detect_api(content):
                    self.entrypoints.append(
                        EntrypointInfo(
                            path=Path(file_path),
                            type="api",
                            language=self._detect_language(file_path),
                            confidence=self._calculate_confidence(content, self.API_PATTERNS),
                            signature=self._extract_signature(content),
                            description=self._describe_entrypoint("api"),
                        )
                    )
                
                if self._detect_cli(content):
                    self.entrypoints.append(
                        EntrypointInfo(
                            path=Path(file_path),
                            type="cli",
                            language=self._detect_language(file_path),
                            confidence=self._calculate_confidence(content, self.CLI_PATTERNS),
                            signature=self._extract_signature(content),
                            description=self._describe_entrypoint("cli"),
                        )
                    )
                
                if self._detect_worker(content):
                    self.entrypoints.append(
                        EntrypointInfo(
                            path=Path(file_path),
                            type="worker",
                            language=self._detect_language(file_path),
                            confidence=self._calculate_confidence(content, self.WORKER_PATTERNS),
                            signature=self._extract_signature(content),
                            description=self._describe_entrypoint("worker"),
                        )
                    )
            except (OSError, UnicodeDecodeError):
                pass
        
        return self.entrypoints
    
    def _detect_main(self, content: str) -> bool:
        """Detect main function entry point."""
        return any(re.search(pattern, content, re.IGNORECASE | re.DOTALL) for pattern in self.MAIN_PATTERNS)
    
    def _detect_api(self, content: str) -> bool:
        """Detect API entry point."""
        return any(re.search(pattern, content, re.IGNORECASE | re.DOTALL) for pattern in self.API_PATTERNS)
    
    def _detect_cli(self, content: str) -> bool:
        """Detect CLI entry point."""
        return any(re.search(pattern, content, re.IGNORECASE | re.DOTALL) for pattern in self.CLI_PATTERNS)
    
    def _detect_worker(self, content: str) -> bool:
        """Detect worker entry point."""
        return any(re.search(pattern, content, re.IGNORECASE | re.DOTALL) for pattern in self.WORKER_PATTERNS)
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript JSX',
            '.jsx': 'JavaScript JSX',
            '.java': 'Java',
            '.cpp': 'C++',
            '.cc': 'C++',
            '.cxx': 'C++',
            '.c': 'C',
            '.rs': 'Rust',
            '.go': 'Go',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
        }
        
        return language_map.get(ext, 'Unknown')
    
    def _calculate_confidence(self, content: str, patterns: List[str]) -> float:
        """
        Calculate confidence score for pattern matching.
        """
        matches = sum(1 for pattern in patterns if re.search(pattern, content, re.IGNORECASE | re.DOTALL))
        return min(matches / len(patterns) if patterns else 0.0, 1.0)
    
    def _extract_signature(self, content: str) -> str:
        """
        Extract the first function/class definition as signature.
        """
        patterns = [
            r'def\s+(\w+)\s*\(',
            r'class\s+(\w+)\s*:',
            r'def\s+main\s*\(',
            r'@app\.(\w+)\s*\(',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "unknown"
    
    def _describe_entrypoint(self, entry_type: str) -> str:
        """
        Get description for entry point type.
        """
        descriptions = {
            "main": "Main application entry point",
            "api": "REST API endpoint",
            "cli": "CLI command-line interface",
            "worker": "Background task handler",
        }
        return descriptions.get(entry_type, "Entry point")