"""
Data models for CodeHist

Simplified data structures for representing chat histories 
focused on core chat functionality.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


@dataclass
class Message:
    """Represents a single message in a chat session"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create Message from dictionary data"""
        timestamp = data.get('timestamp')
        if isinstance(timestamp, str):
            from dateutil.parser import parse
            timestamp = parse(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()
        
        return cls(
            id=data.get('id'),
            role=data.get('role', 'user'),
            content=data.get('content', ''),
            timestamp=timestamp,
            metadata=data.get('metadata', {})
        )


@dataclass
class ChatSession:
    """Represents a chat session with an AI coding agent"""
    agent: str  # e.g., "copilot", "cursor", "windsurf"
    timestamp: datetime
    messages: List[Message] = field(default_factory=list)
    workspace: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'agent': self.agent,
            'timestamp': self.timestamp.isoformat(),
            'messages': [msg.to_dict() for msg in self.messages],
            'workspace': self.workspace,
            'session_id': self.session_id,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """Create ChatSession from dictionary data"""
        timestamp = data.get('timestamp')
        if isinstance(timestamp, str):
            from dateutil.parser import parse
            timestamp = parse(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()
        
        messages = [Message.from_dict(msg) for msg in data.get('messages', [])]
        
        return cls(
            agent=data.get('agent', 'unknown'),
            timestamp=timestamp,
            messages=messages,
            workspace=data.get('workspace'),
            session_id=data.get('session_id'),
            metadata=data.get('metadata', {})
        )


@dataclass
class WorkspaceData:
    """Represents workspace data from an AI coding agent - simplified for chat focus"""
    agent: str
    version: Optional[str] = None
    workspace_path: Optional[str] = None
    chat_sessions: List[ChatSession] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'agent': self.agent,
            'version': self.version,
            'workspace_path': self.workspace_path,
            'chat_sessions': [session.to_dict() for session in self.chat_sessions],
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkspaceData':
        """Create WorkspaceData from dictionary data"""
        chat_sessions = []
        if 'chat_sessions' in data:
            chat_sessions = [ChatSession.from_dict(session_data) for session_data in data['chat_sessions']]
        
        return cls(
            agent=data.get('agent', 'unknown'),
            version=data.get('version'),
            workspace_path=data.get('workspace_path'),
            chat_sessions=chat_sessions,
            metadata=data.get('metadata', {})
        )
