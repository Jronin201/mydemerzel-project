#!/usr/bin/env python3
"""
Script to analyze and optimize embedding files for AI search efficiency.
"""

import json
import numpy as np
import os
import sys
from pathlib import Path
from collections import defaultdict

def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def analyze_embedding_file(file_path):
    """Analyze an embedding file for quality and efficiency."""
    print(f"\n=== ANALYZING {file_path.name} ===")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    size_mb = file_path.stat().st_size / (1024 * 1024)
    print(f"📁 File size: {size_mb:.1f} MB")
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        print(f"📊 Total embeddings: {len(data)}")
        
        if not data:
            print("❌ No embeddings found")
            return
        
        # Analyze structure
        first = data[0]
        required_keys = ['source', 'text', 'embedding']
        for key in required_keys:
            if key not in first:
                print(f"❌ Missing key: {key}")
                return
        
        print(f"✅ Structure valid")
        print(f"📏 Embedding dimensions: {len(first['embedding'])}")
        
        # Analyze text chunks
        text_lengths = [len(item['text']) for item in data]
        avg_length = sum(text_lengths) / len(text_lengths)
        min_length = min(text_lengths)
        max_length = max(text_lengths)
        
        print(f"📝 Text chunk statistics:")
        print(f"   - Average length: {avg_length:.0f} chars")
        print(f"   - Min length: {min_length} chars")
        print(f"   - Max length: {max_length} chars")
        
        # Check for empty or very short chunks
        empty_chunks = sum(1 for length in text_lengths if length < 10)
        if empty_chunks > 0:
            print(f"⚠️  Found {empty_chunks} very short chunks (< 10 chars)")
        
        # Analyze sources
        sources = defaultdict(int)
        for item in data:
            sources[item['source']] += 1
        
        print(f"📚 Sources: {len(sources)}")
        for source, count in sources.items():
            print(f"   - {source}: {count} chunks")
        
        # Sample similarity test (first 100 embeddings)
        sample_size = min(100, len(data))
        sample_embeddings = [np.array(item['embedding']) for item in data[:sample_size]]
        
        # Calculate some similarity scores to check for duplicates
        similarities = []
        for i in range(min(10, sample_size)):
            for j in range(i+1, min(20, sample_size)):
                sim = cosine_similarity(sample_embeddings[i], sample_embeddings[j])
                similarities.append(sim)
        
        if similarities:
            avg_sim = sum(similarities) / len(similarities)
            max_sim = max(similarities)
            print(f"🔍 Sample similarity analysis (first 20 embeddings):")
            print(f"   - Average similarity: {avg_sim:.4f}")
            print(f"   - Max similarity: {max_sim:.4f}")
            
            if max_sim > 0.95:
                print(f"⚠️  High similarity detected - possible duplicates")
            elif avg_sim < 0.1:
                print(f"✅ Good diversity in embeddings")
        
        # Check for potential optimization issues
        print(f"\n🔧 OPTIMIZATION ANALYSIS:")
        
        # Check chunk size distribution
        very_short = sum(1 for length in text_lengths if length < 100)
        very_long = sum(1 for length in text_lengths if length > 2000)
        
        if very_short > len(data) * 0.1:
            print(f"⚠️  {very_short} chunks are very short (< 100 chars) - {very_short/len(data)*100:.1f}%")
            print(f"   Consider merging short chunks for better context")
        
        if very_long > len(data) * 0.1:
            print(f"⚠️  {very_long} chunks are very long (> 2000 chars) - {very_long/len(data)*100:.1f}%")
            print(f"   Consider splitting long chunks for better granularity")
        
        # Check embedding quality
        zero_embeddings = 0
        for item in data[:100]:  # Check first 100
            embedding = np.array(item['embedding'])
            if np.allclose(embedding, 0):
                zero_embeddings += 1
        
        if zero_embeddings > 0:
            print(f"❌ Found {zero_embeddings} zero embeddings in sample")
        else:
            print(f"✅ No zero embeddings detected")
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
    except Exception as e:
        print(f"❌ Error analyzing file: {e}")

def test_search_performance():
    """Test search performance with sample queries."""
    print(f"\n=== SEARCH PERFORMANCE TEST ===")
    
    # Check if we can import OpenAI (optional)
    try:
        from openai import OpenAI
        openai_available = bool(os.environ.get('OPENAI_API_KEY'))
        print(f"🔑 OpenAI available: {openai_available}")
    except ImportError:
        openai_available = False
        print(f"🔑 OpenAI not available")
    
    # Load embeddings
    dune_path = Path('embeddings/dune.json')
    tor_path = Path('embeddings/the-one-ring.json')
    
    if not openai_available:
        print("⚠️  Cannot test live search without OpenAI API key")
        return
    
    try:
        client = OpenAI()
        
        # Test queries for each system
        test_queries = {
            'dune': [
                'Tell me about spice mining on Arrakis',
                'What are the powers of the Bene Gesserit?',
                'How does a stillsuit work?'
            ],
            'the-one-ring': [
                'How do I create a hobbit character?',
                'What are the rules for travel in Middle-earth?',
                'Tell me about the corruption of power'
            ]
        }
        
        for system, queries in test_queries.items():
            emb_file = Path(f'embeddings/{system}.json')
            if not emb_file.exists():
                print(f"⚠️  {system} embeddings not found")
                continue
            
            with open(emb_file, 'r') as f:
                embeddings = json.load(f)
            
            print(f"\n🎮 Testing {system.upper()} system ({len(embeddings)} embeddings)")
            
            for query in queries:
                try:
                    # Generate query embedding
                    response = client.embeddings.create(
                        model="text-embedding-3-small",
                        input=query
                    )
                    query_embedding = response.data[0].embedding
                    
                    # Find best match
                    best_score = -1
                    best_match = None
                    
                    for item in embeddings:
                        score = cosine_similarity(query_embedding, item['embedding'])
                        if score > best_score:
                            best_score = score
                            best_match = item
                    
                    print(f"   Query: '{query}'")
                    print(f"   Best match score: {best_score:.4f}")
                    if best_match:
                        preview = best_match['text'][:150].replace('\n', ' ')
                        print(f"   Preview: {preview}...")
                    print()
                    
                except Exception as e:
                    print(f"   Error testing query '{query}': {e}")
        
    except Exception as e:
        print(f"❌ Error in search performance test: {e}")

def suggest_optimizations():
    """Suggest optimizations based on analysis."""
    print(f"\n=== OPTIMIZATION RECOMMENDATIONS ===")
    
    recommendations = [
        "🎯 SEARCH EFFICIENCY:",
        "   • Ensure chunks are 200-1000 characters for optimal context",
        "   • Remove or merge very short chunks (< 50 chars)",
        "   • Split very long chunks (> 2000 chars) at logical boundaries",
        "",
        "🧠 AI PERFORMANCE:",
        "   • Use semantic boundaries (paragraphs, sections) for chunking",
        "   • Include overlapping context between chunks (50-100 chars)",
        "   • Maintain consistent source attribution",
        "",
        "⚡ SYSTEM OPTIMIZATION:",
        "   • Consider caching frequently accessed embeddings",
        "   • Pre-filter embeddings by source/category if needed",
        "   • Monitor similarity scores to detect quality issues",
        "",
        "🔧 GENERATION IMPROVEMENTS:",
        "   • Use tiktoken for consistent token counting",
        "   • Preserve important formatting and structure",
        "   • Include metadata (page numbers, sections) in source field"
    ]
    
    for rec in recommendations:
        print(rec)

def main():
    """Main analysis function."""
    print("🤖 EMBEDDING ANALYSIS & OPTIMIZATION TOOL")
    print("=" * 50)
    
    # Analyze each embedding file
    for filename in ['dune.json', 'the-one-ring.json']:
        file_path = Path('embeddings') / filename
        analyze_embedding_file(file_path)
    
    # Test search performance
    test_search_performance()
    
    # Provide recommendations
    suggest_optimizations()
    
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    main()
