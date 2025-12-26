"""
AI Semantic Matcher - Uses embeddings for semantic header matching
"""

from typing import Dict, List, Tuple
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from header_mapper.models.column_schema import ColumnSchema


class AISemanticMatcher:
    """AI-powered semantic matching using sentence embeddings"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the AI semantic matcher
        
        Args:
            model_name: Name of the sentence-transformers model to use
                       Default is a lightweight ~80MB model that runs on CPU
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is required for AI semantic matching. "
                "Install it with: pip install sentence-transformers"
            )
        
        self.model = SentenceTransformer(model_name)
        self.schema_embeddings = {}
        self.schema_keys = []
    
    def precompute_schema_embeddings(self, schema: Dict[str, ColumnSchema]) -> None:
        """
        Precompute embeddings for all canonical columns (one-time cost)
        
        Args:
            schema: Dictionary mapping keys to ColumnSchema objects
        """
        texts = []
        keys = []
        
        for key, col_schema in schema.items():
            # Combine name, description, and aliases for richer semantic context
            context_parts = [col_schema.canonical_name]
            
            if col_schema.description:
                context_parts.append(col_schema.description)
            
            if col_schema.aliases:
                context_parts.extend(col_schema.aliases)
            
            text = " ".join(context_parts)
            texts.append(text)
            keys.append(key)
        
        # Encode all schema texts at once (batch processing is faster)
        embeddings = self.model.encode(texts, convert_to_tensor=False, show_progress_bar=False)
        
        # Store embeddings and keys
        self.schema_keys = keys
        for key, embedding in zip(keys, embeddings):
            self.schema_embeddings[key] = embedding
    
    def find_semantic_match(self, user_header: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Find semantically similar canonical columns
        
        Args:
            user_header: The user-provided header to match
            top_k: Number of top matches to return
        
        Returns:
            List of tuples (schema_key, similarity_score) sorted by similarity descending
        """
        if not self.schema_embeddings:
            return []
        
        # Encode user header
        user_embedding = self.model.encode([user_header], convert_to_tensor=False, show_progress_bar=False)[0]
        
        # Calculate cosine similarities
        similarities = {}
        for key, schema_embedding in self.schema_embeddings.items():
            # Cosine similarity using numpy
            similarity = np.dot(user_embedding, schema_embedding) / (
                np.linalg.norm(user_embedding) * np.linalg.norm(schema_embedding)
            )
            similarities[key] = float(similarity)
        
        # Return top matches sorted by similarity
        sorted_matches = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        return sorted_matches[:top_k]
