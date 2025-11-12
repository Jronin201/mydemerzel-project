#!/usr/bin/env python3
"""
Improved embedding generation script for optimal AI search performance.
Addresses the issues found in the analysis:
- Chunks too large (3000+ chars) - reduces granularity
- No overlap between chunks - loses context
- No semantic boundary awareness
"""

import json
import re
import os
from pathlib import Path
from typing import List, Dict, Any
import tiktoken
from openai import OpenAI

# Load environment variables from .env file if it exists
from pathlib import Path
if Path('.env').exists():
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# Optimized parameters based on analysis
OPTIMAL_CHUNK_SIZE = 500  # characters, not tokens (better for search)
MAX_CHUNK_SIZE = 1000     # maximum chunk size
MIN_CHUNK_SIZE = 100      # minimum chunk size
OVERLAP_SIZE = 100        # overlap between chunks for better context
MODEL = "text-embedding-3-small"

class OptimizedEmbeddingGenerator:
    def __init__(self):
        self.client = OpenAI()
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
    def smart_text_splitter(self, text: str, source_name: str) -> List[Dict[str, str]]:
        """
        Split text intelligently using semantic boundaries while maintaining optimal chunk sizes.
        """
        chunks = []
        
        # First, split by major semantic boundaries
        # Look for chapter/section markers, double newlines, etc.
        major_sections = re.split(r'\n\s*\n+', text)
        
        for section_idx, section in enumerate(major_sections):
            section = section.strip()
            if len(section) < MIN_CHUNK_SIZE:
                continue
                
            # If section is already optimal size, use it as is
            if len(section) <= MAX_CHUNK_SIZE:
                chunks.append({
                    'text': section,
                    'source': source_name,
                    'section': section_idx
                })
                continue
            
            # For large sections, split more carefully
            chunks.extend(self._split_large_section(section, source_name, section_idx))
        
        # Add overlapping context between chunks
        chunks_with_overlap = self._add_overlap_context(chunks)
        
        return chunks_with_overlap
    
    def _split_large_section(self, section: str, source_name: str, section_idx: int) -> List[Dict[str, str]]:
        """Split a large section while preserving sentence and paragraph boundaries."""
        chunks = []
        
        # Try to split by paragraphs first
        paragraphs = section.split('\n')
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph would make chunk too large, finalize current chunk
            if current_chunk and len(current_chunk) + len(para) > OPTIMAL_CHUNK_SIZE:
                if len(current_chunk) >= MIN_CHUNK_SIZE:
                    chunks.append({
                        'text': current_chunk.strip(),
                        'source': source_name,
                        'section': section_idx
                    })
                current_chunk = para
            else:
                current_chunk += ("\\n" if current_chunk else "") + para
        
        # Don't forget the last chunk
        if current_chunk and len(current_chunk) >= MIN_CHUNK_SIZE:
            chunks.append({
                'text': current_chunk.strip(),
                'source': source_name,
                'section': section_idx
            })
        
        # If we still have chunks that are too large, split by sentences
        final_chunks = []
        for chunk in chunks:
            if len(chunk['text']) > MAX_CHUNK_SIZE:
                final_chunks.extend(self._split_by_sentences(chunk, source_name, section_idx))
            else:
                final_chunks.append(chunk)
        
        return final_chunks
    
    def _split_by_sentences(self, chunk_data: Dict[str, str], source_name: str, section_idx: int) -> List[Dict[str, str]]:
        """Split large chunks by sentence boundaries."""
        text = chunk_data['text']
        sentences = re.split(r'(?<=[.!?])\\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if current_chunk and len(current_chunk) + len(sentence) > OPTIMAL_CHUNK_SIZE:
                if len(current_chunk) >= MIN_CHUNK_SIZE:
                    chunks.append({
                        'text': current_chunk.strip(),
                        'source': source_name,
                        'section': section_idx
                    })
                current_chunk = sentence
            else:
                current_chunk += (" " if current_chunk else "") + sentence
        
        if current_chunk and len(current_chunk) >= MIN_CHUNK_SIZE:
            chunks.append({
                'text': current_chunk.strip(),
                'source': source_name,
                'section': section_idx
            })
        
        return chunks
    
    def _add_overlap_context(self, chunks: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Add overlapping context between consecutive chunks."""
        if len(chunks) <= 1:
            return chunks
        
        overlapped_chunks = []
        
        for i, chunk in enumerate(chunks):
            text = chunk['text']
            
            # Add context from previous chunk
            if i > 0:
                prev_text = chunks[i-1]['text']
                # Take last OVERLAP_SIZE characters from previous chunk
                if len(prev_text) > OVERLAP_SIZE:
                    overlap_start = prev_text[-OVERLAP_SIZE:]
                    # Find word boundary
                    word_boundary = overlap_start.find(' ')
                    if word_boundary > 0:
                        overlap_start = overlap_start[word_boundary+1:]
                    text = overlap_start + " [...] " + text
            
            # Add context to next chunk (we'll handle this in the next iteration)
            if i < len(chunks) - 1:
                next_text = chunks[i+1]['text']
                # Take first OVERLAP_SIZE characters from next chunk  
                if len(next_text) > OVERLAP_SIZE:
                    overlap_end = next_text[:OVERLAP_SIZE]
                    # Find word boundary
                    word_boundary = overlap_end.rfind(' ')
                    if word_boundary > 0:
                        overlap_end = overlap_end[:word_boundary]
                    text = text + " [...] " + overlap_end
            
            overlapped_chunks.append({
                **chunk,
                'text': text
            })
        
        return overlapped_chunks
    
    def generate_embeddings(self, chunks: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Generate embeddings for text chunks with progress tracking."""
        results = []
        total = len(chunks)
        
        print(f"Generating embeddings for {total} chunks...")
        
        for i, chunk in enumerate(chunks):
            try:
                response = self.client.embeddings.create(
                    model=MODEL,
                    input=chunk['text']
                )
                embedding = response.data[0].embedding
                
                result = {
                    "source": chunk['source'],
                    "text": chunk['text'],
                    "embedding": embedding,
                    "section": chunk.get('section', 0),
                    "chunk_size": len(chunk['text'])
                }
                results.append(result)
                
                if (i + 1) % 10 == 0 or i == total - 1:
                    print(f"  Progress: {i+1}/{total} ({(i+1)/total*100:.1f}%)")
                    
            except Exception as e:
                print(f"  Error processing chunk {i+1}: {e}")
                continue
        
        return results
    
    def process_document(self, input_file: Path, output_file: Path, source_name: str = None):
        """Process a single document file."""
        if not input_file.exists():
            print(f"❌ Input file not found: {input_file}")
            return
        
        if source_name is None:
            source_name = input_file.name
        
        print(f"\\n📖 Processing {input_file.name}")
        print(f"   Source: {source_name}")
        
        # Read the document
        with input_file.open("r", encoding="utf-8") as f:
            text = f.read()
        
        print(f"   Original text: {len(text):,} characters")
        
        # Split into optimized chunks
        chunks = self.smart_text_splitter(text, source_name)
        print(f"   Generated {len(chunks)} optimized chunks")
        
        if chunks:
            avg_size = sum(len(chunk['text']) for chunk in chunks) / len(chunks)
            min_size = min(len(chunk['text']) for chunk in chunks)
            max_size = max(len(chunk['text']) for chunk in chunks)
            print(f"   Chunk sizes: avg={avg_size:.0f}, min={min_size}, max={max_size}")
        
        # Generate embeddings
        results = self.generate_embeddings(chunks)
        
        if not results:
            print(f"❌ No embeddings generated for {input_file}")
            return
        
        # Save results
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        size_mb = output_file.stat().st_size / (1024 * 1024)
        print(f"✅ Saved {len(results)} embeddings to {output_file.name} ({size_mb:.1f} MB)")

def main():
    """Main function to process all documents."""
    print("🚀 OPTIMIZED EMBEDDING GENERATOR")
    print("=" * 50)
    
    generator = OptimizedEmbeddingGenerator()
    
    # Check for API key
    if not os.environ.get('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY environment variable not set")
        return
    
    # Process only new documents (Mouse Guard)
    documents = []
    
    # Mouse Guard documents (new)
    mouse_guard_dir = Path("documents/mouse-guard")
    if mouse_guard_dir.exists():
        for txt_file in mouse_guard_dir.glob("*.txt"):
            # Check if embeddings already exist
            output_file = Path("embeddings/mouse-guard_optimized.json")
            if not output_file.exists():
                documents.append({
                    'input': txt_file,
                    'output': output_file,
                    'source': txt_file.name
                })
            else:
                print(f"✅ Mouse Guard embeddings already exist, skipping")
    
    # Optionally process other documents if their embeddings don't exist
    existing_docs = [
        {
            'input': Path("documents/dune/dune.txt"),
            'output': Path("embeddings/dune_optimized.json"),
            'source': 'dune.txt'
        },
        {
            'input': Path("documents/the-witcher/archive-the-one-ring-starter-rules.txt"),
            'output': Path("embeddings/the-witcher_optimized.json"),
            'source': 'the-witcher-starter-rules.txt'
        }
    ]
    
    for doc in existing_docs:
        if doc['input'].exists() and not doc['output'].exists():
            print(f"📋 Missing embeddings for {doc['source']}, adding to processing queue")
            documents.append(doc)
    
    processed = 0
    for doc in documents:
        if doc['input'].exists():
            generator.process_document(doc['input'], doc['output'], doc['source'])
            processed += 1
        else:
            print(f"⚠️  Skipping {doc['input']} (not found)")
    
    print(f"\\n✅ Processing complete! Generated optimized embeddings for {processed} documents.")
    print(f"\\n💡 Improvements made:")
    print(f"   • Optimal chunk sizes (100-1000 chars vs 3000+ chars)")
    print(f"   • Semantic boundary awareness (paragraphs, sentences)")
    print(f"   • Overlapping context between chunks")
    print(f"   • Better metadata (section info, chunk sizes)")
    print(f"\\n🔄 Replace your original embedding files with the optimized versions")
    print(f"   and restart your application to see improved search performance!")

if __name__ == "__main__":
    main()
