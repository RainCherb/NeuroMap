from __future__ import annotations

import typer
from rich.console import Console
from pathlib import Path

app = typer.Typer(help="NeuroMap — AI-optimized project maps")
console = Console()


@app.command()
def scan(
    path: str = typer.Argument(..., help="Path to the project"),
    level: str = typer.Option("compact", help="Depth level: compact, standard, detailed"),
    max_tokens: int = typer.Option(1000, help="Max tokens for output"),
    format: str = typer.Option("markdown", help="Output format: markdown, json, xml"),
    output: str | None = typer.Option(None, help="Output file"),
):
    """
    Generate a project map optimized for AI.
    """
    from neuromap import __version__
    from .mapper import scan_and_map

    console.print(f"Scanning {path}...")
    console.print(f"   Level: {level}")
    console.print(f"   Max tokens: {max_tokens}")
    console.print(f"   Format: {format}")
    console.print(f"   Output: {output or 'stdout'}")

    neuromap = scan_and_map(Path(path), level=level)
    
    if format == "markdown":
        if level == "compact":
            output_content = neuromap.generate_markdown_compact(max_tokens)
        elif level == "standard":
            output_content = neuromap.generate_markdown_standard(max_tokens)
        elif level == "detailed":
            output_content = neuromap.generate_markdown_detailed(max_tokens)
        else:
            console.print(f"[red]Unknown level: {level}[/red]")
            return
    elif format == "json":
        import json
        output_content = json.dumps(neuromap.get_summary(), indent=2, ensure_ascii=False)
    elif format == "xml":
        # Convert summary to XML
        summary = neuromap.get_summary()
        output_content = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<project_map>\n  <project>\n"
        for key, value in summary.items():
            if isinstance(value, list):
                output_content += f"    <{key}>\n"
                for item in value:
                    output_content += f"      <item>{item}</item>\n"
                output_content += f"    </{key}>\n"
            else:
                output_content += f"    <{key}>{value}</{key}>\n"
        output_content += "  </project>\n</project_map>"
    else:
        console.print(f"[red]Unknown format: {format}[/red]")
        return

    if output:
        Path(output).write_text(output_content)
        console.print(f"[green]Saved to {output}[/green]")
    else:
        console.print(output_content)


@app.command()
def version():
    """Show version"""
    from neuromap import __version__
    console.print(f"NeuroMap v{__version__}")


if __name__ == "__main__":
    app()