"""
Memory-optimized embedding loader for deployment environments with strict memory limits.
This module implements lazy loading and memory-efficient embedding management.
"""

import os
import json
import gc
from pathlib import Path
from typing import List, Dict, Any, Optional
import threading
from functools import lru_cache

class MemoryOptimizedEmbeddingManager:
    """
    Manages embeddings with strict memory optimization for deployment.
    Only loads embeddings when actually needed and implements caching strategies.
    """
    
    def __init__(self, max_cache_size: int = 1):
        """
        Initialize with memory constraints.
        
        Args:
            max_cache_size: Maximum number of embedding sets to keep in memory (default: 1)
        """
        self.max_cache_size = max_cache_size
        self._cache = {}
        self._access_order = []
        self._lock = threading.Lock()
        
        # Available embedding files - updated to match Supabase file names
        self.embedding_files = {
            'dune': {
                'optimized': 'embeddings/dune.json',  # Updated to match Supabase
                'fallback': 'embeddings/dune_fallback.json'
            },
            'the-one-ring': {
                'optimized': 'embeddings/the-one-ring.json',  # Updated to match Supabase
                'fallback': 'embeddings/the-one-ring_fallback.json'
            },
            'mouse-guard': {
                'optimized': 'embeddings/mouse-guard.json',  # Updated to match Supabase
                'fallback': 'embeddings/mouse-guard_fallback.json'
            }
        }
        
        print(f"🧠 Memory-optimized embedding manager initialized (cache size: {max_cache_size})")
    
    def _evict_least_recently_used(self):
        """Remove the least recently used embedding set from cache."""
        if len(self._cache) >= self.max_cache_size and self._access_order:
            lru_key = self._access_order.pop(0)
            if lru_key in self._cache:
                print(f"🧹 Evicting {lru_key} embeddings from memory")
                del self._cache[lru_key]
                # Force garbage collection to free memory immediately
                gc.collect()
    
    def _update_access_order(self, key: str):
        """Update the access order for LRU cache management."""
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
    
    def _load_embedding_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Load embeddings from file with memory optimization."""
        try:
            if not Path(file_path).exists():
                return []
            
            print(f"📂 Loading embeddings from {file_path}")
            file_size = Path(file_path).stat().st_size / (1024 * 1024)  # MB
            print(f"📊 File size: {file_size:.1f}MB")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                embeddings = json.load(f)
            
            print(f"✅ Loaded {len(embeddings)} embedding chunks")
            return embeddings
            
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            return []
    
    def get_embeddings(self, system_name: str) -> List[Dict[str, Any]]:
        """
        Get embeddings for a specific system with lazy loading.
        
        Args:
            system_name: Name of the TTRPG system ('dune', 'the-one-ring', 'mouse-guard')
            
        Returns:
            List of embedding dictionaries
        """
        with self._lock:
            # Check if already in cache
            if system_name in self._cache:
                self._update_access_order(system_name)
                print(f"🎯 Using cached {system_name} embeddings")
                return self._cache[system_name]
            
            # Check if system exists
            if system_name not in self.embedding_files:
                print(f"⚠️  Unknown system: {system_name}")
                return []
            
            # Evict LRU if cache is full
            self._evict_least_recently_used()
            
            # Load embeddings
            system_files = self.embedding_files[system_name]
            
            # Try optimized version first
            embeddings = []
            if Path(system_files['optimized']).exists():
                embeddings = self._load_embedding_file(system_files['optimized'])
            elif Path(system_files['fallback']).exists():
                embeddings = self._load_embedding_file(system_files['fallback'])
            
            # Cache the loaded embeddings
            if embeddings:
                self._cache[system_name] = embeddings
                self._update_access_order(system_name)
                print(f"💾 Cached {system_name} embeddings in memory")
            else:
                print(f"⚠️  No embeddings found for {system_name}")
            
            return embeddings
    
    def preload_system(self, system_name: str):
        """Preload a specific system's embeddings."""
        print(f"🔄 Preloading {system_name} embeddings...")
        self.get_embeddings(system_name)
    
    def clear_cache(self):
        """Clear all cached embeddings and force garbage collection."""
        with self._lock:
            print("🧹 Clearing all embedding cache")
            self._cache.clear()
            self._access_order.clear()
            gc.collect()
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get current cache status for debugging."""
        return {
            'cached_systems': list(self._cache.keys()),
            'cache_size': len(self._cache),
            'max_cache_size': self.max_cache_size,
            'access_order': self._access_order.copy()
        }
    
    def get_memory_usage_estimate(self) -> Dict[str, Any]:
        """Estimate memory usage of currently cached embeddings."""
        total_chunks = sum(len(emb) for emb in self._cache.values())
        estimated_mb = total_chunks * 0.5  # Rough estimate: 0.5KB per chunk
        
        return {
            'cached_systems': len(self._cache),
            'total_chunks': total_chunks,
            'estimated_memory_mb': estimated_mb,
            'systems': {
                name: len(emb) for name, emb in self._cache.items()
            }
        }

# Global instance - only loads embeddings when requested
embedding_manager = MemoryOptimizedEmbeddingManager(max_cache_size=1)

def get_system_embeddings(system_name: str) -> List[Dict[str, Any]]:
    """
    Get embeddings for a specific TTRPG system.
    This is the main function that should be used by the Flask app.
    """
    return embedding_manager.get_embeddings(system_name)

def clear_embedding_cache():
    """Clear embedding cache to free memory."""
    embedding_manager.clear_cache()

def get_embedding_status() -> Dict[str, Any]:
    """Get status of embedding system for debugging."""
    cache_status = embedding_manager.get_cache_status()
    memory_usage = embedding_manager.get_memory_usage_estimate()
    
    # Check which files exist
    file_status = {}
    for system_name, files in embedding_manager.embedding_files.items():
        file_status[system_name] = {
            'optimized_exists': Path(files['optimized']).exists(),
            'fallback_exists': Path(files['fallback']).exists(),
            'optimized_size_mb': Path(files['optimized']).stat().st_size / (1024*1024) if Path(files['optimized']).exists() else 0
        }
    
    return {
        'cache_status': cache_status,
        'memory_usage': memory_usage,
        'file_status': file_status,
        'optimization_active': True
    }

# For backward compatibility with existing code
def load_optimized_embeddings(file_path: str) -> List[Dict[str, Any]]:
    """
    Backward compatibility function.
    Note: This bypasses the memory optimization. Use get_system_embeddings() instead.
    """
    print(f"⚠️  Using legacy load_optimized_embeddings for {file_path}")
    print("   Consider using get_system_embeddings() for better memory efficiency")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        return []
