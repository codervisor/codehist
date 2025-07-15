# CodeHist - GitHub Copilot Chat History Extractor

A simple tool for extracting and analyzing GitHub Copilot chat history from VS Code.

## Features

- **Extract Real Chat History**: Discovers and parses actual GitHub Copilot chat sessions from VS Code data directories
- **Cross-Platform Support**: Works with VS Code, VS Code Insiders, and other variants
- **Multiple Export Formats**: Export to JSON and Markdown
- **Search Functionality**: Search through chat content to find specific conversations
- **Statistics**: View usage statistics and patterns

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd codehist

# Install in development mode
pip install -e .
```

## Usage

### Command Line Interface

```bash
# Show chat statistics
python -m codehist stats

# List all chat sessions
python -m codehist chat

# Search chat content
python -m codehist search "error handling"

# Export to JSON
python -m codehist export --format json --output chat_history.json

# Export to Markdown
python -m codehist export --format markdown --output chat_history.md
```

### Programmatic Usage

```python
from codehist import CopilotParser, JSONExporter

# Parse chat data
parser = CopilotParser()
data = parser.discover_vscode_copilot_data()

# Export to JSON
exporter = JSONExporter()
exporter.export_chat_data(data.to_dict(), Path("output.json"))
```

## How It Works

CodeHist discovers GitHub Copilot chat sessions stored in VS Code's application data:

- **macOS**: `~/Library/Application Support/Code*/User/workspaceStorage/*/chatSessions/`
- **Windows**: `%APPDATA%/Code*/User/workspaceStorage/*/chatSessions/`
- **Linux**: `~/.config/Code*/User/workspaceStorage/*/chatSessions/`

Each chat session is stored as a JSON file containing the conversation between you and GitHub Copilot.

## Data Extracted

- **Chat Sessions**: Complete conversation threads with timestamps
- **Messages**: Individual user and assistant messages with metadata
- **Workspace Context**: Which project/workspace the chat occurred in
- **Session Types**: Different types of interactions (chat, editing sessions, etc.)

## Privacy & Security

- All data parsing happens locally on your machine
- No data is sent to external services
- You control what data is exported and where

## Example Output

```
                       GitHub Copilot Chat Statistics                        
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric         ┃ Value                                                    ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Total Sessions │ 228                                                      │
│ Total Messages │ 880                                                      │
│ Date Range     │ 2025-05-27 to 2025-07-15                               │
└────────────────┴──────────────────────────────────────────────────────────┘

Session Types:
  • chat_editing_session: 116
  • chat_session: 112

Message Types:
  • editing_session: 379
  • snapshot: 116
  • user_request: 385
```

## Architecture

The project is structured for simplicity and focus:

```
codehist/
├── models.py              # Data models (ChatSession, Message, etc.)
├── parsers/
│   └── copilot.py         # GitHub Copilot chat parser
├── exporters/
│   ├── json.py            # JSON export
│   └── markdown.py        # Markdown export
└── cli.py                 # Command-line interface
```

## Contributing

This project focuses specifically on GitHub Copilot chat history extraction. Contributions that enhance this core functionality are welcome.

## License

MIT License - see LICENSE file for details.
