from dataclasses import dataclass, field
from typing import List

@dataclass
class ColumnSchema:
    """Represents a canonical column schema with aliases and metadata"""
    canonical_name: str = ""
    description: str = ""
    data_type: str = ""
    required: bool = False
    example_values: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ColumnSchema':
        """Create a ColumnSchema from a dictionary"""
        return cls(
            canonical_name=data.get('canonicalName', ''),
            description=data.get('description', ''),
            data_type=data.get('dataType', ''),
            required=data.get('required', False),
            example_values=data.get('exampleValues', []),
            aliases=data.get('aliases', [])
        )
