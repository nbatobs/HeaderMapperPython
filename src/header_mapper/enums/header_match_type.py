from enum import Enum

class HeaderMatchType(Enum):
    """Enum representing the type of header match found"""
    EXACT_MATCH = "ExactMatch"
    ALIAS_MATCH = "AliasMatch"
    FUZZY_MATCH = "FuzzyMatch"
    NO_MATCH = "NoMatch"
