from enum import Enum

class MappingAction(Enum):
    """Enum representing the recommended action for a mapping"""
    AUTO_MAP = "AutoMap"
    REVIEW = "Review"
    MANUAL_MAP = "ManualMap"
