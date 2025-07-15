# CodeHist Project - GitHub Copilot Chat History Analysis

## Project Overview

CodeHist is a Python package that extracts and analyzes chat history and workspace data from AI coding assistants. Initially focused on workspace chunks, we've now expanded it to handle **actual GitHub Copilot chat history** from VS Code's SQLite storage.

## What We Discovered

### GitHub Copilot Data Storage Locations

VS Code stores GitHub Copilot data in several locations:

1. **Workspace Chunks** (code embeddings):
   - Location: `{workspace}/GitHub.copilot-chat/workspace-chunks.json`
   - Content: Code chunks with embeddings for context understanding

2. **Chat Editing Sessions** (actual conversations):
   - Location: `~/Library/Application Support/Code/User/workspaceStorage/{workspace_id}/chatEditingSessions/{session_id}/state.json`
   - Content: Actual file editing sessions with GitHub Copilot

3. **SQLite Storage** (UI state and configuration):
   - Location: `~/Library/Application Support/Code/User/workspaceStorage/{workspace_id}/state.vscdb`
   - Content: Chat-related UI state and configuration data

## Key Features Implemented

### 1. Core Parser System
- **CopilotParser**: Handles workspace-chunks.json files (code embeddings)
- **CopilotSQLiteParser**: NEW - Handles chat editing sessions and SQLite storage
- **Unified Data Models**: ChatSession, Message, WorkspaceData, WorkspaceChunk

### 2. CLI Commands
```bash
# Discover all AI agents and their data
python -m codehist discover

# Extract GitHub Copilot chat history
python -m codehist chat

# Export chat history to JSON or Markdown
python -m codehist chat --output history.json
python -m codehist chat --output history.md --format md

# Search within chat conversations
python -m codehist chat --search "Docker"

# Analyze workspace chunks (code embeddings)
python -m codehist scan --agent copilot
python -m codehist analyze workspace-chunks.json
```

### 3. Data Export & Analysis
- **JSON Export**: Structured data export with full metadata
- **Markdown Export**: Human-readable reports
- **Search Functionality**: Search across chat content and metadata
- **Statistics**: Session counts, message types, date ranges

## Live Demo Results

From our testing, we successfully extracted:

### Chat Session Data
- **Session ID**: `00ad0880-2957-4087-8fa8-87f3cb0743d1`
- **Agent**: GitHub Copilot
- **Type**: Chat editing session
- **Files Modified**: 
  - `installation-guide.md` (comprehensive Docker installation guide)
  - `comparison-with-alternatives.md` (comparison between Crawlab and other tools)

### Message Content
The system captured GitHub Copilot's assistance with:
1. Creating installation documentation with Docker commands
2. Building comparison tables between different web crawler management platforms
3. File state tracking and edit history

## Technical Architecture

### Data Models
```python
@dataclass
class Message:
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime
    id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChatSession:
    agent: str
    timestamp: datetime
    messages: List[Message]
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkspaceData:
    agent: str
    chat_sessions: List[ChatSession]
    files: List[FileEntry]  # For workspace chunks
    metadata: Dict[str, Any]
```

### Parser Architecture
- **Base Discovery**: Automatically finds VS Code installation and workspace storage
- **Multi-format Support**: JSON (workspace chunks) + SQLite (state) + File System (sessions)
- **Error Handling**: Graceful handling of missing or corrupted data
- **Cross-platform**: macOS, Windows, Linux support

## Next Steps & Extensibility

### Immediate Enhancements
1. **Enhanced Search**: Search within file edit content in chat sessions
2. **More Chat Types**: Support for inline chat, quick chat, etc.
3. **Conversation Threading**: Link related editing sessions
4. **Visual Analytics**: Generate charts and graphs from chat patterns

### Extension to Other Agents
The architecture is designed to support other AI coding assistants:
- **Cursor**: Chat history and workspace analysis
- **Windsurf**: Session data extraction
- **Codeium**: Conversation history
- **VS Code Extensions**: Any AI assistant that stores data locally

### Advanced Features
1. **Privacy Controls**: Anonymization and data filtering
2. **Team Analytics**: Multi-developer usage patterns
3. **Productivity Metrics**: Measure AI assistant effectiveness
4. **Export Integrations**: Connect to external analytics tools

## Conclusion

We successfully transformed the initial workspace chunks analysis into a comprehensive chat history extraction system. The `codehist` package now provides:

✅ **Real Chat History**: Not just code embeddings, but actual conversations
✅ **Multiple Data Sources**: JSON, SQLite, and file system storage
✅ **Rich Metadata**: Complete context including file edits and session state
✅ **Flexible Export**: JSON and Markdown formats with search capabilities
✅ **Production Ready**: Error handling, logging, and extensible architecture

The system demonstrates that VS Code stores much richer data about AI interactions than initially apparent, and this data can be systematically extracted and analyzed for insights into AI-assisted development workflows.
