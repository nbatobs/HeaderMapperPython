import json
import os
from typing import Dict
from header_mapper.models.column_schema import ColumnSchema

class SchemaLoader:
    """Loads canonical column schemas from JSON files"""
    
    def load_schema(self, json_file_path: str) -> Dict[str, ColumnSchema]:
        """Load schema from a single JSON file"""
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        schema = {}
        for key, value in data.items():
            schema[key] = ColumnSchema.from_dict(value)
        
        return schema
    
    def load_all_schemas(self, directory: str = "aliases") -> Dict[str, ColumnSchema]:
        """Load all schema files from the specified directory"""
        json_files = [
            "feeding-data-alias.json",
            "production-data-alias.json",
            "stirrer-data-alias.json",
            "tank-data-alias.json"
        ]
        
        all_schemas = {}
        
        for file in json_files:
            file_path = os.path.join(directory, file)
            if os.path.exists(file_path):
                schema = self.load_schema(file_path)
                for key, value in schema.items():
                    if key not in all_schemas:
                        all_schemas[key] = value
        
        return all_schemas
