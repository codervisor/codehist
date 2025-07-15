"""
Simplified CLI for CodeHist - Focus on GitHub Copilot Chat History

This is the main entry point focusing on the core chat history extraction functionality.
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table

from .parsers.copilot import CopilotParser
from .exporters.json import JSONExporter
from .exporters.markdown import MarkdownExporter

app = typer.Typer(
    name="codehist",
    help="Extract and analyze GitHub Copilot chat history",
    no_args_is_help=True
)
console = Console()


@app.command()
def chat(
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    format: str = typer.Option("json", "--format", "-f", help="Output format (json, md)"),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search query for chat content"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed progress")
):
    """Extract and analyze GitHub Copilot chat history."""
    try:
        parser = CopilotParser()
        
        if verbose:
            console.print("[yellow]Discovering GitHub Copilot chat data...[/yellow]")
        
        workspace_data = parser.discover_vscode_copilot_data()
        
        if not workspace_data.chat_sessions and not workspace_data.metadata:
            console.print("[red]No GitHub Copilot chat data found[/red]")
            console.print("[yellow]Make sure VS Code or VS Code Insiders is installed and you have used GitHub Copilot chat[/yellow]")
            raise typer.Exit(1)
        
        console.print(f"[green]Found {len(workspace_data.chat_sessions)} chat sessions[/green]")
        
        # Get statistics
        stats = parser.get_chat_statistics(workspace_data)
        
        result = {
            "chat_data": workspace_data.to_dict(),
            "statistics": stats
        }
        
        # Search if query provided
        search_results = []
        if search:
            search_results = parser.search_chat_content(workspace_data, search)
            result["search_results"] = search_results
            console.print(f"[green]Found {len(search_results)} matches for '{search}'[/green]")
        
        # Output results
        if output:
            output_path = Path(output)
            if format == "json":
                exporter = JSONExporter()
                exporter.export_data(result, output_path)
            elif format == "md":
                exporter = MarkdownExporter()
                exporter.export_chat_data(result, output_path)
            else:
                console.print(f"[red]Unsupported format: {format}[/red]")
                raise typer.Exit(1)
            
            console.print(f"[green]Chat data saved to {output_path}[/green]")
        else:
            # Print summary to console
            _display_chat_summary(stats, search_results, verbose)
        
    except Exception as e:
        if verbose:
            console.print_exception()
        else:
            console.print(f"[red]Error extracting chat data: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def stats():
    """Show statistics about available chat data."""
    try:
        parser = CopilotParser()
        workspace_data = parser.discover_vscode_copilot_data()
        
        if not workspace_data.chat_sessions:
            console.print("[red]No chat sessions found[/red]")
            return
        
        stats = parser.get_chat_statistics(workspace_data)
        
        # Display detailed statistics
        table = Table(title="GitHub Copilot Chat Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Sessions", str(stats['total_sessions']))
        table.add_row("Total Messages", str(stats['total_messages']))
        
        if stats["date_range"]["earliest"]:
            table.add_row("Date Range", f"{stats['date_range']['earliest']} to {stats['date_range']['latest']}")
        
        console.print(table)
        
        # Session types
        if stats["session_types"]:
            console.print("\n[bold blue]Session Types:[/bold blue]")
            for session_type, count in stats["session_types"].items():
                console.print(f"  • {session_type}: {count}")
        
        # Message types
        if stats["message_types"]:
            console.print("\n[bold blue]Message Types:[/bold blue]")
            for msg_type, count in stats["message_types"].items():
                console.print(f"  • {msg_type}: {count}")
        
    except Exception as e:
        console.print(f"[red]Error getting statistics: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum results to show"),
    case_sensitive: bool = typer.Option(False, "--case-sensitive", "-c", help="Case sensitive search")
):
    """Search for content in chat history."""
    try:
        parser = CopilotParser()
        workspace_data = parser.discover_vscode_copilot_data()
        
        if not workspace_data.chat_sessions:
            console.print("[red]No chat sessions found[/red]")
            return
        
        search_results = parser.search_chat_content(workspace_data, query, case_sensitive)
        
        if not search_results:
            console.print(f"[yellow]No matches found for '{query}'[/yellow]")
            return
        
        console.print(f"[green]Found {len(search_results)} matches for '{query}'[/green]")
        
        # Display results
        for i, result in enumerate(search_results[:limit], 1):
            console.print(f"\n[bold blue]Match {i}:[/bold blue]")
            console.print(f"  Session: {result['session_id']}")
            console.print(f"  Role: {result['role']}")
            console.print(f"  Context: {result['context'][:200]}...")
        
        if len(search_results) > limit:
            console.print(f"\n[yellow]... and {len(search_results) - limit} more matches[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error searching: {e}[/red]")
        raise typer.Exit(1)


def _display_chat_summary(stats: dict, search_results: list = None, verbose: bool = False):
    """Display a summary of chat statistics."""
    console.print("\n[bold blue]📊 Chat History Summary[/bold blue]")
    console.print(f"Sessions: {stats['total_sessions']}")
    console.print(f"Messages: {stats['total_messages']}")
    
    if stats["date_range"]["earliest"]:
        console.print(f"Date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
    
    if verbose and stats["session_types"]:
        console.print("\n[bold]Session types:[/bold]")
        for session_type, count in stats["session_types"].items():
            console.print(f"  {session_type}: {count}")
    
    if verbose and stats["message_types"]:
        console.print("\n[bold]Message types:[/bold]")
        for msg_type, count in stats["message_types"].items():
            console.print(f"  {msg_type}: {count}")
    
    if search_results:
        console.print(f"\n[green]Search found {len(search_results)} matches[/green]")


def main():
    """Main entry point for the CLI"""
    app()


if __name__ == "__main__":
    main()
