from dataclasses import dataclass
from enums.header_match_type import HeaderMatchType
from enums.mapping_action import MappingAction

@dataclass
class MappingResult:
    """Represents the result of mapping a user column to a canonical column"""
    user_column: str = ""
    canonical_column: str = ""
    confidence: float = 0.0
    match_type: HeaderMatchType = HeaderMatchType.NO_MATCH
    match_details: str = ""
    recommended_action: MappingAction = MappingAction.MANUAL_MAP
    
    def to_dict(self) -> dict:
        """Convert the mapping result to a dictionary for JSON serialization"""
        return {
            "userColumn": self.user_column,
            "canonicalColumn": self.canonical_column,
            "confidence": self.confidence,
            "matchType": self.match_type.value,
            "matchDetails": self.match_details,
            "recommendedAction": self.recommended_action.value
        }
