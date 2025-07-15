"""Tests for CodeHist"""

import pytest
from pathlib import Path
from codehist.core.models import WorkspaceData, FileEntry, WorkspaceChunk, ChunkRange
from codehist.parsers.copilot import CopilotParser


class TestWorkspaceData:
    """Test WorkspaceData model"""
    
    def test_create_workspace_data(self):
        """Test creating WorkspaceData"""
        workspace = WorkspaceData(
            agent="test",
            version="1.0",
            workspace_path="/test/path"
        )
        
        assert workspace.agent == "test"
        assert workspace.version == "1.0"
        assert workspace.workspace_path == "/test/path"
        assert workspace.total_files == 0
        assert workspace.total_chunks == 0
    
    def test_workspace_with_files(self):
        """Test WorkspaceData with files"""
        chunk = WorkspaceChunk(
            text="test code",
            range=ChunkRange(0, 0, 1, 0)
        )
        
        file_entry = FileEntry(
            file_path="/test/file.py",
            chunks=[chunk]
        )
        
        workspace = WorkspaceData(
            agent="test",
            files=[file_entry]
        )
        
        assert workspace.total_files == 1
        assert workspace.total_chunks == 1
        assert len(workspace.get_files_by_extension("py")) == 1


class TestCopilotParser:
    """Test CopilotParser"""
    
    def test_parser_properties(self):
        """Test parser basic properties"""
        parser = CopilotParser()
        
        assert parser.agent_name == "copilot"
        assert "workspace" in parser.supported_data_types
    
    def test_can_parse_invalid_file(self):
        """Test parser with invalid file"""
        parser = CopilotParser()
        
        # Non-existent file
        assert not parser.can_parse(Path("/nonexistent/file.json"))
        
        # Wrong filename
        assert not parser.can_parse(Path("wrong-name.json"))


if __name__ == "__main__":
    pytest.main([__file__])
