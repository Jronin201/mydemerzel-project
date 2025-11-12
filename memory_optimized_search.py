"""
Memory-optimized embedding search with lazy loading.
This module provides the same search functionality but with significantly reduced memory footprint.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from openai import OpenAI
import os
from memory_optimized_embeddings import get_system_embeddings

# Initialize OpenAI client with graceful degradation (tests may not set API key)
try:
    _api_key = os.getenv("OPENAI_API_KEY")
    if not _api_key:
        raise RuntimeError("Missing OPENAI_API_KEY; embedding features disabled for this run")
    client = OpenAI(api_key=_api_key)
except Exception as _e:  # pragma: no cover - defensive path
    print(f"[EMBEDDINGS] OpenAI client unavailable: {_e}")
    client = None

def get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """Get embedding for a text string."""
    if client is None:
        return []
    try:
        response = client.embeddings.create(input=text, model=model)
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Error getting embedding: {e}")
        return []

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not a or not b:
        return 0.0
    
    try:
        # Convert to numpy arrays for efficient computation
        a_arr = np.array(a)
        b_arr = np.array(b)
        
        # Calculate cosine similarity
        dot_product = np.dot(a_arr, b_arr)
        norm_a = np.linalg.norm(a_arr)
        norm_b = np.linalg.norm(b_arr)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    except Exception as e:
        print(f"❌ Error calculating cosine similarity: {e}")
        return 0.0

def memory_optimized_embedding_search(
    query: str,
    system_name: str,
    max_results: int = 5,
    min_similarity: float = 0.6
) -> List[Dict[str, Any]]:
    """
    Search embeddings for a specific TTRPG system with memory optimization.
    
    Args:
        query: Search query text
    system_name: TTRPG system name ('dune', 'the-witcher', 'mouse-guard')
        max_results: Maximum number of results to return
        min_similarity: Minimum similarity threshold
        
    Returns:
        List of matching chunks with similarity scores
    """
    try:
        print(f"🔍 Searching {system_name} embeddings for: '{query[:50]}...'")
        
        # Get query embedding
        query_embedding = get_embedding(query)
        if not query_embedding:
            print("❌ Failed to get query embedding")
            return []
        
        # Lazy load embeddings for the specific system
        embeddings = get_system_embeddings(system_name)
        if not embeddings:
            print(f"⚠️  No embeddings available for {system_name}")
            return []
        
        print(f"🧮 Searching through {len(embeddings)} chunks")
        
        # Calculate similarities and find matches
        matches = []
        for i, chunk in enumerate(embeddings):
            if 'embedding' not in chunk:
                continue
                
            similarity = cosine_similarity(query_embedding, chunk['embedding'])
            
            if similarity >= min_similarity:
                matches.append({
                    'text': chunk.get('text', ''),
                    'similarity': similarity,
                    'source': chunk.get('source', ''),
                    'chunk_id': i,
                    'system': system_name
                })
        
        # Sort by similarity and return top results
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        results = matches[:max_results]
        
        print(f"✅ Found {len(results)} relevant chunks (similarity >= {min_similarity})")
        return results
        
    except Exception as e:
        print(f"❌ Error in embedding search: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return []

def search_multiple_systems(
    query: str,
    systems: List[str],
    max_results_per_system: int = 3,
    min_similarity: float = 0.6
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Search across multiple TTRPG systems efficiently.
    This loads one system at a time to minimize memory usage.
    
    Args:
        query: Search query text
        systems: List of system names to search
        max_results_per_system: Max results per system
        min_similarity: Minimum similarity threshold
        
    Returns:
        Dictionary mapping system names to search results
    """
    results = {}
    
    for system in systems:
        print(f"🎯 Searching {system}...")
        system_results = memory_optimized_embedding_search(
            query, system, max_results_per_system, min_similarity
        )
        if system_results:
            results[system] = system_results
        
        # Optional: Clear cache between systems to save memory
        # Uncomment this line if memory is extremely tight
        # from memory_optimized_embeddings import clear_embedding_cache
        # clear_embedding_cache()
    
    return results

def get_best_matches_across_systems(
    query: str,
    systems: List[str],
    max_total_results: int = 5,
    min_similarity: float = 0.6
) -> List[Dict[str, Any]]:
    """
    Get the best matches across all specified systems.
    
    Args:
        query: Search query text
        systems: List of system names to search
        max_total_results: Maximum total results to return
        min_similarity: Minimum similarity threshold
        
    Returns:
        Combined list of best matches sorted by similarity
    """
    all_results = []
    
    # Search each system
    for system in systems:
        system_results = memory_optimized_embedding_search(
            query, system, max_total_results * 2, min_similarity
        )
        all_results.extend(system_results)
    
    # Sort all results by similarity and return top matches
    all_results.sort(key=lambda x: x['similarity'], reverse=True)
    return all_results[:max_total_results]

# Backward compatibility function
def improved_embedding_search(
    query: str,
    embeddings: List[Dict[str, Any]],
    max_results: int = 5,
    min_similarity: float = 0.6
) -> List[Dict[str, Any]]:
    """
    Backward compatibility function for existing code.
    Note: This doesn't use memory optimization since embeddings are already loaded.
    """
    try:
        print(f"🔍 Legacy search through {len(embeddings)} embeddings")
        
        # Get query embedding
        query_embedding = get_embedding(query)
        if not query_embedding:
            return []
        
        # Calculate similarities
        matches = []
        for i, chunk in enumerate(embeddings):
            if 'embedding' not in chunk:
                continue
                
            similarity = cosine_similarity(query_embedding, chunk['embedding'])
            
            if similarity >= min_similarity:
                matches.append({
                    'text': chunk.get('text', ''),
                    'similarity': similarity,
                    'source': chunk.get('source', ''),
                    'chunk_id': i
                })
        
        # Sort and return top results
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        return matches[:max_results]
        
    except Exception as e:
        print(f"❌ Error in legacy embedding search: {e}")
        return []
