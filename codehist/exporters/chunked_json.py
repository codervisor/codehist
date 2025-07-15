"""
Chunked JSON exporter for CodeHist chat data using pandas

Handles large chat session exports by processing data in chunks to manage memory usage.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Optional, Iterator
from datetime import datetime
import tempfile
import os

from ..models import ChatSession, Message, WorkspaceData


class ChunkedJSONExporter:
    """JSON exporter that processes large chat data in chunks using pandas"""
    
    def __init__(self, chunk_size: int = 100):
        """
        Initialize chunked exporter
        
        Args:
            chunk_size: Number of chat sessions to process per chunk
        """
        self.chunk_size = chunk_size
    
    def export_data_chunked(
        self, 
        data: Dict[str, Any], 
        output_path: Path,
        chunk_sessions: bool = True,
        chunk_messages: bool = True
    ) -> None:
        """
        Export data in chunks to manage memory usage
        
        Args:
            data: Full data dictionary containing chat_data and statistics
            output_path: Path to output file
            chunk_sessions: Whether to chunk by sessions
            chunk_messages: Whether to chunk messages within sessions
        """
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Extract chat sessions
        chat_data = data.get('chat_data', {})
        chat_sessions = chat_data.get('chat_sessions', [])
        
        if not chat_sessions:
            # No sessions to chunk, export normally
            self._export_simple(data, output_path)
            return
        
        print(f"Processing {len(chat_sessions)} sessions in chunks of {self.chunk_size}")
        
        # Create temporary directory for chunk files
        with tempfile.TemporaryDirectory() as temp_dir:
            chunk_files = []
            
            # Process sessions in chunks
            for chunk_idx, session_chunk in enumerate(self._chunk_sessions(chat_sessions)):
                chunk_file = Path(temp_dir) / f"chunk_{chunk_idx:04d}.json"
                chunk_files.append(chunk_file)
                
                # Process chunk using pandas
                self._process_chunk_with_pandas(
                    session_chunk, 
                    chunk_file,
                    chunk_messages=chunk_messages
                )
                
                print(f"Processed chunk {chunk_idx + 1}/{(len(chat_sessions) + self.chunk_size - 1) // self.chunk_size}")
            
            # Combine chunks into final output
            self._combine_chunks(chunk_files, data, output_path)
    
    def _chunk_sessions(self, sessions: List[Dict]) -> Iterator[List[Dict]]:
        """Split sessions into chunks"""
        for i in range(0, len(sessions), self.chunk_size):
            yield sessions[i:i + self.chunk_size]
    
    def _process_chunk_with_pandas(
        self, 
        session_chunk: List[Dict], 
        chunk_file: Path,
        chunk_messages: bool = True
    ) -> None:
        """Process a chunk of sessions using pandas for efficient handling"""
        processed_sessions = []
        
        for session_dict in session_chunk:
            # Convert messages to DataFrame for efficient processing
            messages = session_dict.get('messages', [])
            
            if messages and chunk_messages:
                # Create DataFrame from messages
                df_messages = pd.DataFrame(messages)
                
                # Process messages in smaller chunks if needed
                if len(df_messages) > 1000:  # Large session
                    processed_messages = []
                    for msg_chunk in self._chunk_dataframe(df_messages, 1000):
                        processed_messages.extend(msg_chunk.to_dict('records'))
                    session_dict['messages'] = processed_messages
                else:
                    # Convert back to dict records
                    session_dict['messages'] = df_messages.to_dict('records')
            
            processed_sessions.append(session_dict)
        
        # Write chunk to file
        with open(chunk_file, 'w', encoding='utf-8') as f:
            json.dump(processed_sessions, f, indent=2, default=self._json_serializer)
    
    def _chunk_dataframe(self, df: pd.DataFrame, chunk_size: int) -> Iterator[pd.DataFrame]:
        """Split DataFrame into chunks"""
        for i in range(0, len(df), chunk_size):
            yield df.iloc[i:i + chunk_size]
    
    def _combine_chunks(self, chunk_files: List[Path], original_data: Dict, output_path: Path) -> None:
        """Combine processed chunks into final output file"""
        print("Combining chunks into final output...")
        
        # Start building final structure
        final_data = {
            'statistics': original_data.get('statistics', {}),
            'search_results': original_data.get('search_results', []),
            'chat_data': {
                'agent': original_data.get('chat_data', {}).get('agent', 'GitHub Copilot'),
                'version': original_data.get('chat_data', {}).get('version'),
                'workspace_path': original_data.get('chat_data', {}).get('workspace_path'),
                'metadata': original_data.get('chat_data', {}).get('metadata', {}),
                'chat_sessions': []
            }
        }
        
        # Read and combine chunks
        total_sessions = 0
        for chunk_file in chunk_files:
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunk_sessions = json.load(f)
                final_data['chat_data']['chat_sessions'].extend(chunk_sessions)
                total_sessions += len(chunk_sessions)
        
        print(f"Combined {total_sessions} sessions from {len(chunk_files)} chunks")
        
        # Write final output
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2, default=self._json_serializer)
    
    def export_sessions_to_csv(
        self, 
        workspace_data: WorkspaceData, 
        output_path: Path,
        include_message_content: bool = False
    ) -> None:
        """
        Export session metadata to CSV for easier analysis
        
        Args:
            workspace_data: Workspace data containing sessions
            output_path: Path to CSV output file
            include_message_content: Whether to include full message content
        """
        sessions_data = []
        
        for session in workspace_data.chat_sessions:
            session_info = {
                'session_id': session.session_id,
                'agent': session.agent,
                'timestamp': session.timestamp,
                'workspace': session.workspace,
                'message_count': len(session.messages),
                'user_messages': len([m for m in session.messages if m.role == 'user']),
                'assistant_messages': len([m for m in session.messages if m.role == 'assistant']),
                'system_messages': len([m for m in session.messages if m.role == 'system']),
                'total_chars': sum(len(m.content) for m in session.messages),
                'avg_message_length': sum(len(m.content) for m in session.messages) / len(session.messages) if session.messages else 0
            }
            
            if include_message_content:
                # Add sample of first user message
                user_messages = [m for m in session.messages if m.role == 'user']
                if user_messages:
                    first_user_msg = user_messages[0].content[:200]  # First 200 chars
                    session_info['first_user_message'] = first_user_msg
            
            sessions_data.append(session_info)
        
        # Create DataFrame and export to CSV
        df = pd.DataFrame(sessions_data)
        df.to_csv(output_path, index=False)
        print(f"Exported {len(sessions_data)} session summaries to {output_path}")
    
    def export_messages_to_parquet(
        self, 
        workspace_data: WorkspaceData, 
        output_path: Path,
        chunk_size: int = 10000
    ) -> None:
        """
        Export all messages to Parquet format for efficient storage and querying
        
        Args:
            workspace_data: Workspace data containing sessions
            output_path: Path to Parquet output file
            chunk_size: Number of messages per chunk
        """
        all_messages = []
        
        for session in workspace_data.chat_sessions:
            for message in session.messages:
                message_data = {
                    'session_id': session.session_id,
                    'message_id': message.id,
                    'role': message.role,
                    'content': message.content,
                    'timestamp': message.timestamp,
                    'content_length': len(message.content),
                    'agent': session.agent,
                    'workspace': session.workspace
                }
                all_messages.append(message_data)
        
        # Create DataFrame
        df = pd.DataFrame(all_messages)
        
        # Export to Parquet (automatically compressed)
        df.to_parquet(output_path, index=False)
        print(f"Exported {len(all_messages)} messages to {output_path}")
        print(f"Original size would be ~{len(str(all_messages)) / 1024 / 1024:.1f}MB, Parquet is much smaller")
    
    def _export_simple(self, data: Dict[str, Any], output_path: Path) -> None:
        """Simple export fallback for small datasets"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=self._json_serializer)
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for objects that aren't JSON serializable by default"""
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):  # Generic objects
            return obj.__dict__
        else:
            return str(obj)


def analyze_json_file_chunks(file_path: Path, chunk_size: int = 1000) -> Dict[str, Any]:
    """
    Analyze a large JSON file by reading it in chunks
    
    Args:
        file_path: Path to JSON file
        chunk_size: Number of sessions to read per chunk
    
    Returns:
        Analysis results
    """
    try:
        # Read just the structure first
        with open(file_path, 'r') as f:
            # Read first part to get structure
            partial_content = f.read(10000)  # First 10KB
            
        if 'chat_sessions' in partial_content:
            print(f"File {file_path.name} appears to contain chat session data")
            
            # For large files, we could implement streaming JSON parsing
            # For now, let's get basic file info
            file_size = file_path.stat().st_size
            print(f"File size: {file_size / 1024 / 1024:.1f} MB")
            
            return {
                'file_size_mb': file_size / 1024 / 1024,
                'contains_sessions': True,
                'analysis_method': 'partial_read'
            }
        
    except Exception as e:
        print(f"Error analyzing file: {e}")
        return {'error': str(e)}
