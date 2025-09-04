"""
Optimized embedding search functions for improved AI performance.
"""

import numpy as np
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def semantic_search(
    query_embedding: List[float], 
    embeddings: List[Dict[str, Any]], 
    top_k: int = 3,
    min_similarity: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Perform semantic search with improved ranking and filtering.
    
    Args:
        query_embedding: The embedding vector for the search query
        embeddings: List of embedding dictionaries with 'embedding', 'text', etc.
        top_k: Number of top results to return
        min_similarity: Minimum similarity score to consider
    
    Returns:
        List of top matching chunks with scores and metadata
    """
    if not embeddings:
        return []
    
    # Calculate similarities
    results = []
    for item in embeddings:
        similarity = cosine_similarity(query_embedding, item['embedding'])
        
        if similarity >= min_similarity:
            result = {
                'text': item['text'],
                'source': item['source'],
                'similarity': float(similarity),
                'chunk_size': item.get('chunk_size', len(item['text'])),
                'section': item.get('section', 0)
            }
            results.append(result)
    
    # Sort by similarity (descending)
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Return top_k results
    return results[:top_k]

def diversified_search(
    query_embedding: List[float], 
    embeddings: List[Dict[str, Any]], 
    top_k: int = 3,
    diversity_threshold: float = 0.8
) -> List[Dict[str, Any]]:
    """
    Perform search with diversity filtering to avoid redundant results.
    
    Args:
        query_embedding: The embedding vector for the search query
        embeddings: List of embedding dictionaries
        top_k: Number of results to return
        diversity_threshold: Minimum difference between selected results
    
    Returns:
        Diverse set of top matching chunks
    """
    # Get initial candidates
    candidates = semantic_search(query_embedding, embeddings, top_k * 3)
    
    if not candidates:
        return []
    
    # Select diverse results
    selected = [candidates[0]]  # Always include the best match
    
    for candidate in candidates[1:]:
        if len(selected) >= top_k:
            break
        
        # Check if this candidate is diverse enough from selected results
        is_diverse = True
        for selected_item in selected:
            # Calculate similarity between candidate and selected item
            # Use text embedding similarity as a proxy for content similarity
            candidate_emb = next(
                (item['embedding'] for item in embeddings if item['text'] == candidate['text']), 
                None
            )
            selected_emb = next(
                (item['embedding'] for item in embeddings if item['text'] == selected_item['text']), 
                None
            )
            
            if candidate_emb and selected_emb:
                inter_similarity = cosine_similarity(candidate_emb, selected_emb)
                if inter_similarity > diversity_threshold:
                    is_diverse = False
                    break
        
        if is_diverse:
            selected.append(candidate)
    
    return selected

def context_aware_search(
    query_embedding: List[float], 
    embeddings: List[Dict[str, Any]], 
    context_keywords: List[str] = None,
    boost_recent: bool = False,
    top_k: int = 3
) -> List[Dict[str, Any]]:
    """
    Enhanced search with context awareness and keyword boosting.
    
    Args:
        query_embedding: The embedding vector for the search query
        embeddings: List of embedding dictionaries
        context_keywords: List of keywords to boost in ranking
        boost_recent: Whether to boost more recent sections
        top_k: Number of results to return
    
    Returns:
        Context-aware ranked results
    """
    results = semantic_search(query_embedding, embeddings, top_k * 2)
    
    if not results:
        return results
    
    # Apply context-based boosting
    for result in results:
        boost_factor = 1.0
        text_lower = result['text'].lower()
        
        # Keyword boosting
        if context_keywords:
            keyword_matches = sum(1 for keyword in context_keywords if keyword.lower() in text_lower)
            if keyword_matches > 0:
                boost_factor += 0.1 * keyword_matches
        
        # Section boosting (prefer earlier sections for foundational content)
        if boost_recent and 'section' in result:
            # Slight boost for later sections (assumes they contain more specific info)
            section_boost = min(0.05, result['section'] * 0.01)
            boost_factor += section_boost
        
        # Length penalty for very long chunks (they may be less focused)
        chunk_size = result.get('chunk_size', len(result['text']))
        if chunk_size > 1500:
            boost_factor *= 0.95
        elif chunk_size < 200:
            boost_factor *= 0.9  # Also penalize very short chunks
        
        # Apply boost to similarity score
        result['boosted_similarity'] = result['similarity'] * boost_factor
        result['boost_factor'] = boost_factor
    
    # Re-sort by boosted similarity
    results.sort(key=lambda x: x['boosted_similarity'], reverse=True)
    
    return results[:top_k]

def format_search_results_for_prompt(
    results: List[Dict[str, Any]], 
    max_total_length: int = 3000,
    include_sources: bool = True
) -> str:
    """
    Format search results for inclusion in AI prompt.
    
    Args:
        results: List of search results
        max_total_length: Maximum total character length
        include_sources: Whether to include source attribution
    
    Returns:
        Formatted text for AI prompt
    """
    if not results:
        return ""
    
    formatted_parts = []
    total_length = 0
    
    for i, result in enumerate(results):
        text = result['text']
        source = result['source']
        similarity = result['similarity']
        
        # Create header
        if include_sources:
            header = f"[REFERENCE {i+1} - {source} (similarity: {similarity:.3f})]"
        else:
            header = f"[REFERENCE {i+1}]"
        
        # Check if we can fit this result
        result_length = len(header) + len(text) + 10  # +10 for spacing
        if total_length + result_length > max_total_length and i > 0:
            break
        
        formatted_parts.append(f"{header}\\n{text}")
        total_length += result_length
    
    return "\\n\\n".join(formatted_parts)

# Improved search integration for the main app
def improved_embedding_search(
    query: str,
    query_embedding: List[float],
    embeddings: List[Dict[str, Any]],
    ttrpg_type: str = "",
    context_keywords: List[str] = None
) -> str:
    """
    Main search function that combines all improvements.
    
    Args:
        query: Original user query
        query_embedding: Embedding vector for the query
        embeddings: Available embeddings
        ttrpg_type: Type of TTRPG (for context-specific boosting)
        context_keywords: Keywords for boosting
    
    Returns:
        Formatted reference text for AI prompt
    """
    if not embeddings:
        return ""
    
    # Define context keywords based on TTRPG type
    if not context_keywords:
        context_keywords = []
        if ttrpg_type == "dune":
            context_keywords = ["spice", "arrakis", "house", "bene gesserit", "fremen"]
        elif ttrpg_type == "the-one-ring":
            context_keywords = ["witcher", "mutagen", "signs", "contract", "alchemy"]
    
    # Perform enhanced search
    results = context_aware_search(
        query_embedding=query_embedding,
        embeddings=embeddings,
        context_keywords=context_keywords,
        boost_recent=False,  # Prefer foundational content for TTRPGs
        top_k=3
    )
    
    # Format for AI prompt
    formatted_text = format_search_results_for_prompt(
        results=results,
        max_total_length=2500,  # Leave room for other prompt content
        include_sources=True
    )
    
    return formatted_text

def load_optimized_embeddings(file_path: str) -> List[Dict[str, Any]]:
    """Load embeddings with error handling and validation."""
    try:
        path = Path(file_path)
        if not path.exists():
            print(f"Warning: Embedding file not found: {file_path}")
            return []
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            print(f"Warning: Empty embedding file: {file_path}")
            return []
        
        # Validate structure
        required_keys = ['text', 'embedding', 'source']
        if not all(key in data[0] for key in required_keys):
            print(f"Warning: Invalid embedding structure in {file_path}")
            return []
        
        print(f"Loaded {len(data)} embeddings from {path.name}")
        return data
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        return []
    except Exception as e:
        print(f"Error loading embeddings from {file_path}: {e}")
        return []
