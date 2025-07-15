"""
Simple Markdown exporter for CodeHist chat data

Simplified version without complex configuration.
"""

from pathlib import Path
from typing import Any, Dict
from datetime import datetime


class MarkdownExporter:
    """Simple Markdown exporter for chat data"""
    
    def export_chat_data(self, data: Dict[str, Any], output_path: Path) -> None:
        """Export chat data to Markdown file"""
        sections = []
        
        # Header
        sections.append("# GitHub Copilot Chat History")
        sections.append("")
        sections.append(f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sections.append("")
        
        # Statistics
        stats = data.get("statistics", {})
        if stats:
            sections.append("## Summary")
            sections.append("")
            sections.append(f"- **Total Sessions:** {stats.get('total_sessions', 0)}")
            sections.append(f"- **Total Messages:** {stats.get('total_messages', 0)}")
            
            if stats.get("date_range", {}).get("earliest"):
                sections.append(f"- **Date Range:** {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
            
            sections.append("")
        
        # Chat data
        chat_data = data.get("chat_data", {})
        if chat_data and chat_data.get("chat_sessions"):
            sections.append("## Chat Sessions")
            sections.append("")
            
            for i, session in enumerate(chat_data["chat_sessions"], 1):
                if i > 10:  # Limit to first 10 sessions to avoid huge files
                    sections.append(f"... and {len(chat_data['chat_sessions']) - 10} more sessions")
                    break
                    
                sessions_id = session.get('session_id', 'Unknown')[:8]  # Truncate for readability
                sections.append(f"### Session {i}: {sessions_id}")
                sections.append("")
                sections.append(f"- **Agent:** {session.get('agent', 'Unknown')}")
                sections.append(f"- **Timestamp:** {session.get('timestamp', 'Unknown')}")
                sections.append(f"- **Messages:** {len(session.get('messages', []))}")
                sections.append("")
                
                # Messages (limit to first few)
                messages = session.get("messages", [])
                for j, msg in enumerate(messages[:3], 1):  # Show first 3 messages
                    role = msg.get('role', 'Unknown').title()
                    sections.append(f"#### Message {j} ({role})")
                    sections.append("")
                    content = msg.get('content', '')
                    if len(content) > 500:
                        content = content[:500] + "... [TRUNCATED]"
                    sections.append(f"```")
                    sections.append(content)
                    sections.append(f"```")
                    sections.append("")
                
                if len(messages) > 3:
                    sections.append(f"... and {len(messages) - 3} more messages")
                    sections.append("")
        
        # Search results
        search_results = data.get("search_results", [])
        if search_results:
            sections.append("## Search Results")
            sections.append("")
            
            for i, result in enumerate(search_results[:20], 1):  # Limit to 20 results
                sections.append(f"### Match {i}")
                sections.append("")
                sections.append(f"- **Session:** {result.get('session_id', 'Unknown')[:8]}")
                sections.append(f"- **Role:** {result.get('role', 'Unknown')}")
                sections.append("")
                sections.append("**Context:**")
                sections.append("")
                sections.append(f"```")
                sections.append(result.get('context', ''))
                sections.append(f"```")
                sections.append("")
            
            if len(search_results) > 20:
                sections.append(f"... and {len(search_results) - 20} more matches")
        
        markdown_content = "\n".join(sections)
        
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
