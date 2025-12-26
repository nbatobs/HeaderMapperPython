from dataclasses import dataclass

@dataclass
class ThresholdConfig:
    """Configuration for confidence thresholds"""
    auto_map_threshold: float = 0.85
    review_threshold: float = 0.70

@dataclass
class MatchingConfig:
    """Configuration for header matching behavior"""
    fuzzy_min_threshold: int = 60
    required_thresholds: ThresholdConfig = None
    optional_thresholds: ThresholdConfig = None
    
    def __post_init__(self):
        if self.required_thresholds is None:
            self.required_thresholds = ThresholdConfig(
                auto_map_threshold=0.90,
                review_threshold=0.75
            )
        if self.optional_thresholds is None:
            self.optional_thresholds = ThresholdConfig(
                auto_map_threshold=0.85,
                review_threshold=0.70
            )
