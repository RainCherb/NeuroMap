# NeuroMap — AI-Optimized Project Maps for Understanding Large Codebases

[![Build](https://img.shields.io/github/actions/workflow/status/RainCherb/NeuroMap/test.yml)](https://github.com/RainCherb/NeuroMap/actions)
[![Python](https://img.shields.io/pypi/pyversions/neuro-map.svg)](https://pypi.org/project/neuro-map)
[![License](https://img.shields.io/github/license/RainCherb/NeuroMap.svg)](https://github.com/RainCherb/NeuroMap/blob/main/LICENSE)

## About

When codebases become very large with many files, AI models start to get confused and lost. **NeuroMap** creates a detailed project map that an AI can easily read even with a small amount of context.

It breaks down everything for the AI so it can start understanding the essence and structure of the project.

## Installation

```bash
pip install neuromap
```

Or with dev dependencies:

```bash
pip install neuromap[dev]
```

## Quick Start

### Creating a Map

```bash
# Quick compact map (~500 tokens)
neuromap scan ./my-project

# Standard map with token limit
neuromap scan ./my-project --level standard --max-tokens 2000

# Full detailed map in JSON
neuromap scan ./my-project --level detailed --format json -o ai_context.json
```

### Usage Examples

#### 1. Compact Map for General Understanding

```bash
neuromap scan ./my-project --level compact --format markdown
```

Output (example):
```markdown
# my-project

**Languages:** Python 3.11
**Total files:** 42
**Code lines:** 1578
**Directories:** 7

## Entry Points
- `src/main.py`: Main application entry point
- `src/api/router.py`: REST API router

## Key Symbols
- `Engine.process` in engine.py (function)
- `UserModel` in models.py (class)
```

#### 2. Standard Map for Development

```bash
neuromap scan ./my-project --level standard --format json > project_context.json
```

#### 3. Detailed Map for Architecture Overview

```bash
neuromap scan ./my-project --level detailed --format markdown --output PROJECT_MAP.md
```

Output contains:
- Full annotated file tree
- Complete symbol index with signatures
- Dependency visualization
- Architecture analysis

## Output Formats

### Markdown
Perfectly readable by both humans and AI. Contains structured project information.

### JSON
Machine-readable format, perfect for building tools on top of NeuroMap.

### XML
Standardized format for system prompts and integration with other tools.

## Configuration

### Configuration File

Create `.neuromap/config.json`:

```json
{
  "default_level": "compact",
  "default_max_tokens": 1000,
  "default_format": "markdown",
  "exclude_patterns": ["*.test.*", "__pycache__", ".git"],
  "include_patterns": [],
  "entrypoints": {
    "detect_main": true,
    "detect_api": true,
    "detect_cli": true,
    "detect_worker": true
  }
}
```

### Custom Config via CLI

```bash
neuromap config set default_level standard
neuromap config set default_max_tokens 2000
```

## Supported Languages

- **Python** (3.11+)
- **JavaScript / TypeScript** (ES6+)
- **Java** (8+)
- **C / C++**
- **Rust**
- **Go**
- **PHP**
- **Ruby**
- **Swift**
- **Kotlin**

## Architecture Detectors

### Entry Points
- **Main** — Main entry point (`main()`)
- **API** — REST API endpoints (FastAPI, Django, Spring)
- **CLI** — Command line interface (Click, Typer)
- **Worker** — Background tasks (Celery, Daphne)

### Frameworks
- **FastAPI** — Modern APIs
- **Django** / **DRF** — Classic web frameworks
- **Spring** — Java ecosystem
- **React** — Frontend (via JSX parsers)

### Patterns
- **MVC** — Model-View-Controller
- **Clean Architecture** — Layered responsibilities
- **Microservices** — Service visualization
- **Monolithic** — Single application structure

## Technologies

- **Typer** — Modern CLI framework
- **Rich** — Beautiful terminal output
- **Tree-sitter** — Code parsing (integration in progress)
- **NetworkX** — Dependency graph
- **Tiktoken** — Token counting
- **Pydantic** — Data validation

## AI Backend (Future Plans)

NeuroMap can be extended with the following modules:

1. **Graph Neural Networks** — Architecture analysis
2. **Code2Query** — AI query generation
3. **PatternLearner** — Learning from architectural patterns
4. **ImpactAnalyzer** — Change impact analysis

## License

MIT

## Contributing

We welcome contributions! Please read the [contributing guidelines](./CONTRIBUTING.md) before submitting a pull request.

## Contact

- Discord: [neuromap.ai/discord](https://neuromap.ai/discord)
- Twitter: [@neuromap_ai](https://twitter.com/neuromap_ai)
- GitHub: [RainCherb/NeuroMap](https://github.com/RainCherb/NeuroMap)

## Notes

This project uses:
- `tree-sitter` for code parsing (to be added in the next version)
- `NetworkX` for building dependency graphs
- `Tiktoken` for accurate token counting
- `Pydantic` for configuration validation
