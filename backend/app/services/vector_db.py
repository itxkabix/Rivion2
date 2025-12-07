import os
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Lazy load Pinecone (only when needed, not at import)
_pc = None
_index = None

def _get_pinecone():
    """Initialize Pinecone only when first needed"""
    global _pc, _index
    if _pc is None:
        try:
            from pinecone import Pinecone
            api_key = os.environ.get("PINECONE_API_KEY")
            if not api_key:
                logger.warning("PINECONE_API_KEY not set - vector DB disabled")
                return None, None
            
            _pc = Pinecone(api_key=api_key)
            _index = _pc.Index(os.environ.get("PINECONE_INDEX"))
            logger.info("Pinecone initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            return None, None
    
    return _pc, _index

async def store_embedding(session_id: str, embedding: List[float], metadata: Dict[str, Any]) -> str:
    """Store face embedding in Pinecone"""
    try:
        pc, index = _get_pinecone()
        if index is None:
            logger.warning("Pinecone not available, skipping embedding storage")
            return None
        
        # Create unique ID for vector
        vector_id = f"session_{session_id}_{metadata.get('timestamp', 'unknown')}"
        
        # Upsert vector to Pinecone
        index.upsert(
            vectors=[
                (vector_id, embedding, metadata)
            ]
        )
        
        logger.info(f"Stored embedding: {vector_id}")
        return vector_id
    except Exception as e:
        logger.error(f"Error storing embedding: {e}")
        raise

async def search_similar_faces(embedding: List[float], top_k: int = 10) -> List[Dict]:
    """Search for similar face embeddings"""
    try:
        pc, index = _get_pinecone()
        if index is None:
            logger.warning("Pinecone not available, returning empty results")
            return []
        
        # Query Pinecone
        results = index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Format results
        matches = []
        for match in results.get('matches', []):
            matches.append({
                'session_id': match['metadata'].get('session_id'),
                'similarity': match['score'],
                'metadata': match['metadata']
            })
        
        logger.info(f"Found {len(matches)} similar faces")
        return matches
    except Exception as e:
        logger.error(f"Error searching embeddings: {e}")
        raise

async def delete_session_vectors(session_id: str) -> bool:
    """Delete all vectors for a session (privacy)"""
    try:
        pc, index = _get_pinecone()
        if index is None:
            logger.warning("Pinecone not available, skipping cleanup")
            return True
        
        # Query by metadata
        results = index.query(
            vector=[0] * 512,  # Dummy vector
            top_k=10000,
            filter={"session_id": {"$eq": session_id}},
            include_metadata=True
        )
        
        # Delete matching vectors
        vector_ids = [match['id'] for match in results.get('matches', [])]
        if vector_ids:
            index.delete(ids=vector_ids)
            logger.info(f"Deleted {len(vector_ids)} vectors for session {session_id}")
        
        return True
    except Exception as e:
        logger.error(f"Error deleting vectors: {e}")
        raise
