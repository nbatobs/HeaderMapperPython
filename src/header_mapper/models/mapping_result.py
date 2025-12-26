from dataclasses import dataclass
from header_mapper.enums.header_match_type import HeaderMatchType
from header_mapper.enums.mapping_action import MappingAction

@dataclass
class MappingResult:
    """Represents the result of mapping a user column to a canonical column"""
    user_column: str = ""
    canonical_column: str = ""
    confidence: float = 0.0
    recommended_action: MappingAction = MappingAction.MANUAL_MAP
    
    def to_dict(self) -> dict:
        """Convert the mapping result to a dictionary for JSON serialization"""
        return {
            "userColumn": self.user_column,
            "canonicalColumn": self.canonical_column,
            "confidence": self.confidence,
            "recommendedAction": self.recommended_action.value
        }
