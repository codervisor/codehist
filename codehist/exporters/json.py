"""
Simple JSON exporter for CodeHist chat data

Simplified version without complex configuration.
"""

import json
from pathlib import Path
from typing import Any, Dict
from datetime import datetime


class JSONExporter:
    """Simple JSON exporter for chat data"""
    
    def export_data(self, data: Dict[str, Any], output_path: Path) -> None:
        """Export arbitrary data to JSON file"""
        # Get JSON export options
        json_options = {
            "indent": 2,
            "ensure_ascii": False
        }
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, **json_options, default=self._json_serializer)
    
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
