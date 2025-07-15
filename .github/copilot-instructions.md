# CodeHist - AI Coding Instructions

CodeHist extracts GitHub Copilot chat history from VS Code's JSON storage files.

## Core Architecture

**Purpose**: Parse real chat conversations from `workspaceStorage/*/chatSessions/*.json`, not SQLite metadata.

**Key Components**:
- `models.py` - Dataclasses: `Message`, `ChatSession`, `WorkspaceData`
- `parsers/copilot.py` - Single parser with cross-platform VS Code discovery
- `exporters/` - Simple JSON/Markdown output
- `cli.py` - Typer CLI with 3 commands: `stats`, `chat`, `search`

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

### Testing Commands
```bash
python -m codehist stats              # Show session count
python -m codehist search "docker"    # Test search
python -m codehist chat -o test.json  # Export validation
```

## Key Constraints

- **No SQLite**: Recently removed - focus on JSON parsing only
- **Single Purpose**: GitHub Copilot only, not multi-agent
- **No Complex Config**: Keep exporters and CLI simple
- **Dataclasses over Pydantic**: Current pattern for models

Avoid re-introducing complexity that was recently removed from the multi-agent version.
