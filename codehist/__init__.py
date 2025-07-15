"""
CodeHist - AI Coding Agent History Extractor

A tool for extracting and analyzing chat history from AI coding agents
like GitHub Copilot, Cursor, and Windsurf.

This package provides:
- Parsing capabilities for different agent data formats
- Unified data models for chat sessions and messages  
- Export functionality to JSON and Markdown
- CLI for easy interaction

Focus is on GitHub Copilot chat history extraction.
"""

__version__ = "0.1.0"
__author__ = "codervisor"
__email__ = "codervisor@example.com"

from .models import ChatSession, Message, WorkspaceData
from .parsers.copilot import CopilotParser
from .exporters.json import JSONExporter
from .exporters.markdown import MarkdownExporter

__all__ = [
    "ChatSession",
    "Message", 
    "WorkspaceData",
    "CopilotParser",
    "JSONExporter",
    "MarkdownExporter",
]
