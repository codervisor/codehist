# Getting Started with CodeHist

## Overview

CodeHist is a universal parser for AI coding agent chat histories and workspace data. This guide will help you get started with the tool.

## Installation

### From Source (Development)

```bash
git clone https://github.com/codervisor/codehist.git
cd codehist
pip install -e .
```

### From PyPI (Coming Soon)

```bash
pip install codehist
```

## Quick Start

### 1. Discover AI Agents

First, discover what AI coding agents are installed on your system:

```bash
codehist discover
```

For detailed information:

```bash
codehist discover --verbose
```

### 2. Analyze Agent Data

Analyze workspace data from a specific agent:

```bash
codehist analyze copilot
```

### 3. Search Content

Search across all agent data:

```bash
codehist search "function definition"
```

Search within a specific agent:

```bash
codehist search "class" --agent copilot --limit 5
```

### 4. Export Data

Export to JSON:

```bash
codehist export --agent copilot --format json --output copilot_data.json
```

Export to Markdown:

```bash
codehist export --agent copilot --format markdown --output copilot_report.md
```

Export without embeddings (smaller file size):

```bash
codehist export --agent copilot --no-embeddings --output copilot_summary.json
```

### 5. Scan All Agents

Scan and parse data from all available agents:

```bash
codehist scan
```

Scan a specific agent with verbose output:

```bash
codehist scan --agent copilot --verbose
```

## Configuration

### View Current Configuration

```bash
codehist config --show
```

### Modify Configuration

```bash
codehist config --set "default_output_format=markdown"
codehist config --set "include_embeddings=false"
codehist config --set "anonymize_paths=true"
```

### Reset to Defaults

```bash
codehist config --reset
```

## Supported AI Agents

- ✅ **GitHub Copilot** (VS Code workspace chunks)
- 🚧 **Cursor** (coming soon)
- 🚧 **Windsurf** (coming soon)  
- 🚧 **Cline** (coming soon)
- 🚧 **Claude Desktop** (coming soon)
- 🚧 **Continue.dev** (coming soon)

## Example Workflows

### Daily Coding Summary

Generate a daily summary of your coding activity:

```bash
# Export today's data
codehist export --date-range $(date +%Y-%m-%d):$(date +%Y-%m-%d) --format markdown --output daily_summary.md

# Analyze patterns
codehist analyze copilot --detailed --output daily_analysis.json
```

### Project Documentation

Export project workspace data for documentation:

```bash
# Export without embeddings for documentation
codehist export --agent copilot --no-embeddings --format markdown --output project_overview.md

# Search for specific patterns
codehist search "TODO\|FIXME\|HACK" --case-sensitive
```

### Code Review Preparation

Prepare data for code review:

```bash
# Export recent changes
codehist export --date-range 2024-01-01:2024-12-31 --format json --output review_data.json

# Analyze complexity
codehist analyze copilot --detailed
```

## Privacy and Security

CodeHist operates entirely locally and never sends data to external services:

- ✅ **Local Processing**: All data stays on your machine
- ✅ **No Network Calls**: No data transmitted externally
- ✅ **Configurable Privacy**: Choose what to include/exclude
- ✅ **Path Anonymization**: Option to anonymize file paths

### Privacy Settings

```bash
# Enable path anonymization
codehist config --set "anonymize_paths=true"

# Exclude sensitive patterns
codehist config --set "exclude_patterns=['*/secrets/*', '*/private/*']"

# Disable metadata inclusion
codehist config --set "include_metadata=false"
```

## Troubleshooting

### No Agents Found

If no agents are discovered:

1. Ensure the agents are installed and have been used
2. Check that workspace data exists
3. Try running the agents to generate data

### Permission Errors

If you encounter permission errors:

```bash
# Check file permissions
ls -la ~/.config/codehist/

# Reset configuration
codehist config --reset
```

### Large File Exports

For large workspaces:

```bash
# Exclude embeddings to reduce size
codehist export --no-embeddings

# Use date range filtering
codehist export --date-range 2024-01-01:2024-03-31
```

## Advanced Usage

### Python API

```python
from codehist.core.discovery import AgentDiscovery
from codehist.parsers.copilot import CopilotParser
from codehist.utils.analyzer import WorkspaceAnalyzer

# Discover agents
discovery = AgentDiscovery()
agents = discovery.discover_all()

# Parse copilot data
parser = CopilotParser()
workspace_data = parser.parse_workspace_data(data_file_path)

# Analyze
analyzer = WorkspaceAnalyzer()
analysis = analyzer.analyze(workspace_data)

print(f"Primary language: {analysis.summary['primary_language']}")
```

### Custom Analysis

```python
from codehist.parsers.copilot import CopilotParser

parser = CopilotParser()
workspace_data = parser.parse_workspace_data("path/to/workspace-chunks.json")

# Custom search
results = parser.search_workspace_content(workspace_data, "async function")

# File statistics
stats = parser.get_workspace_statistics(workspace_data)
print(f"File types: {stats['file_extensions']}")
```

## Contributing

CodeHist is open source and welcomes contributions:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Setup

```bash
git clone https://github.com/codervisor/codehist.git
cd codehist
pip install -e ".[dev]"
pytest
```

## Support

- 📖 [Documentation](https://github.com/codervisor/codehist/docs)
- 🐛 [Issue Tracker](https://github.com/codervisor/codehist/issues)
- 💬 [Discussions](https://github.com/codervisor/codehist/discussions)

## License

CodeHist is licensed under the MIT License. See [LICENSE](LICENSE) for details.
