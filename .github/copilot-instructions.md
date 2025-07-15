# CodeHist - AI Coding Instructions

CodeHist extracts GitHub Copilot chat history from VS Code's JSON storage files.

## Core Architecture

**Purpose**: Parse real chat conversations from `workspaceStorage/*/chatSessions/*.json`, not SQLite metadata.

**Key Components**:
- `codehist/models.py` - Dataclasses: `Message`, `ChatSession`, `WorkspaceData`
- `codehist/parsers/copilot.py` - Single parser with cross-platform VS Code discovery
- `codehist/exporters/` - Simple JSON/Markdown output
- `codehist/cli.py` - Typer CLI with 3 commands: `stats`, `chat`, `search`

## Development SOPs

### Data Models
- Use `@dataclass` with `to_dict()`/`from_dict()` methods
- Rich metadata in `Message.metadata` dict
- No complex configuration objects

### VS Code Discovery Pattern
```python
# Cross-platform paths for VS Code data
vscode_paths = [
    "~/Library/Application Support/Code*/User",      # macOS
    "%APPDATA%/Code*/User",                          # Windows  
    "~/.config/Code*/User"                           # Linux
]
```

### Session Types
- `chatSessions/*.json` - Modern chat conversations
- `chatEditingSessions/*/state.json` - Legacy editing sessions

### Dependency Management
```bash
uv sync                                       # Install dependencies
uv add <package>                             # Add new dependency
uv remove <package>                          # Remove dependency
```

### Testing Commands
```bash
uv run python -m codehist stats              # Show session count
uv run python -m codehist search "docker"    # Test search
uv run python -m codehist chat -o test.json  # Export validation
```

### File Organization
- **Temporary Files**: Use `tmp/` folder for all temporary scripts, data files, and test outputs
- **Git Ignore**: The `tmp/` folder is not committed to git - safe for experiments and debugging
- **Examples**: `tmp/test_output.json`, `tmp/debug_script.py`, `tmp/sample_sessions/`

## Key Constraints

- **No SQLite**: Recently removed - focus on JSON parsing only
- **Single Purpose**: GitHub Copilot only, not multi-agent
- **No Complex Config**: Keep exporters and CLI simple
- **Dataclasses over Pydantic**: Current pattern for models

Avoid re-introducing complexity that was recently removed from the multi-agent version.
