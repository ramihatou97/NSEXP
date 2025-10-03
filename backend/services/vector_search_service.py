"""
Vector Search Service for Neurosurgical Knowledge System
Provides semantic search functionality using FAISS
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("FAISS not available. Vector search will use fallback methods.")

class VectorSearchService:
    def __init__(self, vector_dim: int = 1536):
        self.vector_dim = vector_dim
        self.index = None
        if FAISS_AVAILABLE:
            import faiss
            self.index = faiss.IndexFlatIP(vector_dim)
    
    async def get_index_stats(self) -> Dict[str, Any]:
        return {
            "faiss_available": FAISS_AVAILABLE,
            "total_documents": self.index.ntotal if self.index else 0,
            "vector_dimension": self.vector_dim
        }

def get_vector_search_service() -> VectorSearchService:
    return VectorSearchService()

