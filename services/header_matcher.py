from typing import Dict, List, Optional
from fuzzywuzzy import fuzz
from models.column_schema import ColumnSchema
from models.mapping_result import MappingResult
from models.matching_config import MatchingConfig
from enums.header_match_type import HeaderMatchType
from enums.mapping_action import MappingAction

class HeaderMatcher:
    """Matches user-provided headers to canonical schema columns"""
    
    def __init__(self, schema: Dict[str, ColumnSchema], config: Optional[MatchingConfig] = None):
        self.schema = schema
        self.config = config if config is not None else MatchingConfig()
    
    def map_headers(self, user_headers: List[str]) -> List[MappingResult]:
        """Map a list of user headers to canonical columns"""
        results = []
        for user_header in user_headers:
            result = self.map_single_header(user_header)
            results.append(result)
        return results
    
    def map_single_header(self, user_header: str) -> MappingResult:
        """Map a single user header to a canonical column"""
        normalized_user_header = self._normalize_header(user_header)
        
        # Layer 1: Exact match
        for key, schema in self.schema.items():
            if self._normalize_header(schema.canonical_name) == normalized_user_header:
                return MappingResult(
                    user_column=user_header,
                    canonical_column=schema.canonical_name,
                    confidence=1.0,
                    match_type=HeaderMatchType.EXACT_MATCH,
                    match_details="Exact match to canonical name",
                    recommended_action=MappingAction.AUTO_MAP
                )
        
        # Layer 2: Alias match
        for key, schema in self.schema.items():
            for alias in schema.aliases:
                if self._normalize_header(alias) == normalized_user_header:
                    return MappingResult(
                        user_column=user_header,
                        canonical_column=schema.canonical_name,
                        confidence=0.95,
                        match_type=HeaderMatchType.ALIAS_MATCH,
                        match_details=f"Matched alias: '{alias}'",
                        recommended_action=MappingAction.AUTO_MAP
                    )
        
        # Layer 3: Fuzzy matching
        best_match = self._find_best_fuzzy_match(user_header, normalized_user_header)
        
        if best_match:
            return best_match
        
        # No match found
        return MappingResult(
            user_column=user_header,
            canonical_column="",
            confidence=0.0,
            match_type=HeaderMatchType.NO_MATCH,
            match_details="No suitable match found",
            recommended_action=MappingAction.MANUAL_MAP
        )
    
    def _find_best_fuzzy_match(self, user_header: str, normalized_user_header: str) -> Optional[MappingResult]:
        """Find the best fuzzy match for a user header"""
        candidates = []
        
        for key, schema in self.schema.items():
            # Compare against canonical name
            canonical_score = fuzz.ratio(
                normalized_user_header,
                self._normalize_header(schema.canonical_name)
            )
            candidates.append((schema.canonical_name, schema.canonical_name, canonical_score, schema.required))
            
            # Compare against aliases
            for alias in schema.aliases:
                alias_score = fuzz.ratio(
                    normalized_user_header,
                    self._normalize_header(alias)
                )
                candidates.append((schema.canonical_name, alias, alias_score, schema.required))
            
            # Compare against description (token-based for semantic similarity)
            description_score = fuzz.token_set_ratio(
                normalized_user_header,
                self._normalize_header(schema.description)
            )
            # Lower weight for description matches
            candidates.append((
                schema.canonical_name,
                f"description: {schema.description}",
                description_score // 2,
                schema.required
            ))
        
        # Find best match
        if not candidates:
            return None
        
        best = max(candidates, key=lambda x: x[2])
        canonical, target, score, is_required = best
        
        if score >= self.config.fuzzy_min_threshold:
            confidence = score / 100.0
            action = self._determine_action(confidence, is_required)
            
            return MappingResult(
                user_column=user_header,
                canonical_column=canonical,
                confidence=confidence,
                match_type=HeaderMatchType.FUZZY_MATCH,
                match_details=f"Fuzzy match against '{target}' (score: {score})",
                recommended_action=action
            )
        
        return None
    
    def _normalize_header(self, header: str) -> str:
        """Normalize a header string for comparison"""
        if not header:
            return ""
        
        return (header
                .lower()
                .replace("_", " ")
                .replace("-", " ")
                .replace(".", " ")
                .replace("(", " ")
                .replace(")", " ")
                .replace("/", " ")
                .strip()
                .replace("  ", " "))
    
    def _determine_action(self, confidence: float, is_required: bool) -> MappingAction:
        """Determine the recommended action based on confidence and requirement status"""
        thresholds = (self.config.required_thresholds if is_required 
                     else self.config.optional_thresholds)
        
        if confidence >= thresholds.auto_map_threshold:
            return MappingAction.AUTO_MAP
        elif confidence >= thresholds.review_threshold:
            return MappingAction.REVIEW
        else:
            return MappingAction.MANUAL_MAP
    
    def get_top_matches(self, user_header: str, top_n: int = 3) -> List[MappingResult]:
        """Get the top N matches for a user header"""
        normalized_user_header = self._normalize_header(user_header)
        candidates = []
        
        for key, schema in self.schema.items():
            canonical_score = fuzz.ratio(
                normalized_user_header,
                self._normalize_header(schema.canonical_name)
            )
            
            max_alias_score = 0
            best_alias = ""
            for alias in schema.aliases:
                alias_score = fuzz.ratio(
                    normalized_user_header,
                    self._normalize_header(alias)
                )
                if alias_score > max_alias_score:
                    max_alias_score = alias_score
                    best_alias = alias
            
            best_score = max(canonical_score, max_alias_score)
            match_target = best_alias if max_alias_score > canonical_score else schema.canonical_name
            
            if best_score >= self.config.fuzzy_min_threshold:
                candidates.append(MappingResult(
                    user_column=user_header,
                    canonical_column=schema.canonical_name,
                    confidence=best_score / 100.0,
                    match_type=HeaderMatchType.FUZZY_MATCH,
                    match_details=f"Matched against '{match_target}'",
                    recommended_action=self._determine_action(best_score / 100.0, schema.required)
                ))
        
        return sorted(candidates, key=lambda x: x.confidence, reverse=True)[:top_n]
