"""
GitHub Copilot chat history parser for VS Code

This module handles parsing GitHub Copilot chat sessions from VS Code's
JSON storage files to extract actual conversation history.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from ..models import ChatSession, Message, WorkspaceData

logger = logging.getLogger(__name__)


class CopilotParser:
    """Parser for GitHub Copilot chat sessions from VS Code storage."""
    
    def __init__(self):
        self.logger = logger
        
    def parse_chat_session(self, file_path: Path) -> Optional[ChatSession]:
        """Parse actual chat session from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            session_id = data.get('sessionId', file_path.stem)
            
            # Parse timestamps
            creation_date = data.get('creationDate')
            last_message_date = data.get('lastMessageDate')
            
            if creation_date:
                try:
                    timestamp = datetime.fromisoformat(creation_date.replace('Z', '+00:00'))
                except:
                    timestamp = datetime.fromtimestamp(file_path.stat().st_mtime)
            else:
                timestamp = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            # Extract messages from requests
            messages = []
            for request in data.get('requests', []):
                # User message
                user_message_text = request.get('message', {}).get('text', '')
                if user_message_text:
                    user_message = Message(
                        role="user",
                        content=user_message_text,
                        timestamp=timestamp,
                        id=request.get('requestId'),
                        metadata={
                            'type': 'user_request',
                            'agent': request.get('agent', {}),
                            'variableData': request.get('variableData', {}),
                            'modelId': request.get('modelId')
                        }
                    )
                    messages.append(user_message)
                
                # Assistant response
                response = request.get('response')
                if response:
                    # Handle different response formats
                    response_text = ""
                    if isinstance(response, dict):
                        if 'value' in response:
                            response_text = response['value']
                        elif 'text' in response:
                            response_text = response['text']
                        elif 'content' in response:
                            response_text = response['content']
                    elif isinstance(response, str):
                        response_text = response
                    
                    if response_text:
                        assistant_message = Message(
                            role="assistant",
                            content=response_text,
                            timestamp=timestamp,
                            id=request.get('responseId'),
                            metadata={
                                'type': 'assistant_response',
                                'result': request.get('result', {}),
                                'followups': request.get('followups', []),
                                'isCanceled': request.get('isCanceled', False),
                                'contentReferences': request.get('contentReferences', []),
                                'codeCitations': request.get('codeCitations', []),
                                'requestTimestamp': request.get('timestamp')
                            }
                        )
                        messages.append(assistant_message)
            
            session = ChatSession(
                agent="GitHub Copilot",
                timestamp=timestamp,
                messages=messages,
                workspace=None,
                session_id=session_id,
                metadata={
                    'version': data.get('version'),
                    'requesterUsername': data.get('requesterUsername'),
                    'responderUsername': data.get('responderUsername'),
                    'initialLocation': data.get('initialLocation'),
                    'creationDate': creation_date,
                    'lastMessageDate': last_message_date,
                    'isImported': data.get('isImported'),
                    'customTitle': data.get('customTitle'),
                    'type': 'chat_session',
                    'source_file': str(file_path),
                    'total_requests': len(data.get('requests', []))
                }
            )
            
            self.logger.info(f"Parsed chat session {session_id} with {len(messages)} messages")
            return session
            
        except Exception as e:
            self.logger.error(f"Error parsing chat session {file_path}: {e}")
            return None
    
    def parse_chat_editing_session(self, file_path: Path) -> Optional[ChatSession]:
        """Parse chat editing session from state.json file (legacy format)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            session_id = data.get('sessionId', '')
            timestamp = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            # Extract messages from linear history
            messages = []
            for i, history_entry in enumerate(data.get('linearHistory', [])):
                # Create a message for each history entry
                request_id = history_entry.get('requestId', f'request_{i}')
                working_set = history_entry.get('workingSet', [])
                entries = history_entry.get('entries', [])
                
                # This is a file editing session, so create a descriptive message
                content = f"Chat editing session with {len(working_set)} files in working set"
                if entries:
                    content += f" and {len(entries)} entries"
                
                message = Message(
                    role="system",
                    content=content,
                    timestamp=timestamp,
                    id=request_id,
                    metadata={
                        'workingSet': working_set,
                        'entries': entries,
                        'type': 'editing_session'
                    }
                )
                messages.append(message)
            
            # Also add information about recent snapshot
            recent_snapshot = data.get('recentSnapshot', {})
            if recent_snapshot:
                snapshot_message = Message(
                    role="system",
                    content=f"Recent snapshot with {len(recent_snapshot.get('workingSet', []))} files",
                    timestamp=timestamp,
                    id=f"snapshot_{session_id}",
                    metadata={
                        'recentSnapshot': recent_snapshot,
                        'type': 'snapshot'
                    }
                )
                messages.append(snapshot_message)
            
            session = ChatSession(
                agent="GitHub Copilot",
                timestamp=timestamp,
                messages=messages,
                workspace=None,
                session_id=session_id,
                metadata={
                    'version': data.get('version'),
                    'linearHistoryIndex': data.get('linearHistoryIndex'),
                    'initialFileContents': data.get('initialFileContents', []),
                    'recentSnapshot': recent_snapshot,
                    'type': 'chat_editing_session',
                    'source_file': str(file_path)
                }
            )
            
            self.logger.info(f"Parsed chat editing session {session_id} with {len(messages)} entries")
            return session
            
        except Exception as e:
            self.logger.error(f"Error parsing chat editing session {file_path}: {e}")
            return None
    
    def discover_vscode_copilot_data(self) -> WorkspaceData:
        """Discover Copilot data from VS Code's application support directory."""
        import os
        
        # Get VS Code storage paths (including Insiders)
        vscode_paths = []
        if os.name == 'nt':  # Windows
            base_home = Path.home() / "AppData/Roaming"
            vscode_paths = [
                base_home / "Code/User",
                base_home / "Code - Insiders/User"
            ]
        elif os.uname().sysname == 'Darwin':  # macOS
            base_home = Path.home() / "Library/Application Support"
            vscode_paths = [
                base_home / "Code/User",
                base_home / "Code - Insiders/User"
            ]
        else:  # Linux
            base_home = Path.home() / ".config"
            vscode_paths = [
                base_home / "Code/User",
                base_home / "Code - Insiders/User"
            ]
        
        # Collect all data from all VS Code installations
        all_data = WorkspaceData(agent="GitHub Copilot")
        
        for base_path in vscode_paths:
            if base_path.exists():
                self.logger.info(f"Discovering Copilot data from: {base_path}")
                data = self.discover_copilot_data(base_path)
                if data.chat_sessions:
                    # Merge the data
                    all_data.chat_sessions.extend(data.chat_sessions)
                    all_data.workspace_path = str(base_path)  # Use the last successful path
                    # Merge metadata
                    for key, value in data.metadata.items():
                        if key in all_data.metadata:
                            if isinstance(all_data.metadata[key], list) and isinstance(value, list):
                                all_data.metadata[key].extend(value)
                            else:
                                all_data.metadata[f"{key}_{base_path.name}"] = value
                        else:
                            all_data.metadata[key] = value
        
        if not all_data.chat_sessions:
            self.logger.warning("No chat sessions found in any VS Code installation")
        else:
            self.logger.info(f"Total discovered: {len(all_data.chat_sessions)} chat sessions")
        
        return all_data
    
    def discover_copilot_data(self, base_path: Path) -> WorkspaceData:
        """Discover and parse all Copilot data in a directory."""
        workspace_data = WorkspaceData(
            agent="GitHub Copilot",
            workspace_path=str(base_path),
            metadata={'discovery_source': str(base_path)}
        )
        
        # Look for actual chat session JSON files (new format)
        chat_session_pattern = "workspaceStorage/*/chatSessions/*.json"
        for session_file in base_path.glob(chat_session_pattern):
            session = self.parse_chat_session(session_file)
            if session:
                workspace_data.chat_sessions.append(session)
        
        # Look for chat editing session files (legacy format)
        editing_session_pattern = "workspaceStorage/*/chatEditingSessions/*/state.json"
        for session_file in base_path.glob(editing_session_pattern):
            session = self.parse_chat_editing_session(session_file)
            if session:
                workspace_data.chat_sessions.append(session)
        
        self.logger.info(f"Discovered {len(workspace_data.chat_sessions)} chat sessions from {base_path}")
        return workspace_data
    
    def search_chat_content(self, workspace_data: WorkspaceData, query: str, 
                           case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Search for content in chat sessions."""
        results = []
        search_query = query if case_sensitive else query.lower()
        
        for session in workspace_data.chat_sessions:
            for message in session.messages:
                content = message.content if case_sensitive else message.content.lower()
                
                if search_query in content:
                    # Find context around the match
                    match_pos = content.find(search_query)
                    context_start = max(0, match_pos - 100)
                    context_end = min(len(content), match_pos + len(search_query) + 100)
                    context = content[context_start:context_end]
                    
                    results.append({
                        "session_id": session.session_id,
                        "message_id": message.id,
                        "role": message.role,
                        "timestamp": message.timestamp.isoformat(),
                        "match_position": match_pos,
                        "context": context,
                        "full_content": message.content,
                        "metadata": message.metadata
                    })
        
        return results
    
    def get_chat_statistics(self, workspace_data: WorkspaceData) -> Dict[str, Any]:
        """Get statistics about chat sessions."""
        stats = {
            "total_sessions": len(workspace_data.chat_sessions),
            "total_messages": 0,
            "message_types": {},
            "session_types": {},
            "date_range": {
                "earliest": None,
                "latest": None
            },
            "agent_activity": {}
        }
        
        all_timestamps = []
        
        for session in workspace_data.chat_sessions:
            session_type = session.metadata.get('type', 'unknown')
            stats["session_types"][session_type] = stats["session_types"].get(session_type, 0) + 1
            
            all_timestamps.append(session.timestamp)
            
            agent = session.agent
            stats["agent_activity"][agent] = stats["agent_activity"].get(agent, 0) + 1
            
            for message in session.messages:
                stats["total_messages"] += 1
                
                message_type = message.metadata.get('type', message.role)
                stats["message_types"][message_type] = stats["message_types"].get(message_type, 0) + 1
                
                all_timestamps.append(message.timestamp)
        
        if all_timestamps:
            stats["date_range"]["earliest"] = min(all_timestamps).isoformat()
            stats["date_range"]["latest"] = max(all_timestamps).isoformat()
        
        return stats
