#!/usr/bin/env python3
"""
Script to update app.py with optimized embedding search functionality.
"""

import shutil
from pathlib import Path

def backup_current_app():
    """Create a backup of the current app.py"""
    backup_path = Path("app_backup.py")
    if backup_path.exists():
        backup_path = Path(f"app_backup_{Path('app.py').stat().st_mtime:.0f}.py")
    
    shutil.copy2("app.py", backup_path)
    print(f"✅ Created backup: {backup_path}")
    return backup_path

def update_app_imports():
    """Add the new import for optimized search"""
    with open("app.py", "r") as f:
        content = f.read()
    
    # Add import after existing imports
    import_line = "from optimized_embedding_search import improved_embedding_search, load_optimized_embeddings"
    
    if import_line not in content:
        # Find a good place to add the import (after other local imports)
        import_insertion_point = content.find("from user_character_info import")
        if import_insertion_point != -1:
            # Find end of that line
            line_end = content.find("\\n", import_insertion_point)
            if line_end != -1:
                content = content[:line_end] + "\\n" + import_line + content[line_end:]
        else:
            # Fallback: add after the last import
            last_import = content.rfind("import ")
            if last_import != -1:
                line_end = content.find("\\n", last_import)
                if line_end != -1:
                    content = content[:line_end] + "\\n" + import_line + content[line_end:]
    
    with open("app.py", "w") as f:
        f.write(content)
    
    print("✅ Added optimized search import")

def update_embedding_loading():
    """Update the embedding loading to use optimized versions when available"""
    with open("app.py", "r") as f:
        content = f.read()
    
    # Replace the embedding loading section
    old_tor_loading = '''the_witcher_embeddings = []
if Path("embeddings/the-witcher.json").exists():
    with open("embeddings/the-witcher.json", "r", encoding="utf-8") as f:
        the_witcher_embeddings = json.load(f)'''
    
    new_tor_loading = '''# Load The Witcher embeddings (prefer optimized version)
the_witcher_embeddings = []
optimized_tor_path = "embeddings/the-witcher_optimized.json"
fallback_tor_path = "embeddings/the-witcher.json"

if Path(optimized_tor_path).exists():
    the_witcher_embeddings = load_optimized_embeddings(optimized_tor_path)
    print("📚 Loaded optimized The Witcher embeddings")
elif Path(fallback_tor_path).exists():
    the_witcher_embeddings = load_optimized_embeddings(fallback_tor_path)
    print("📚 Loaded standard The Witcher embeddings")'''
    
    old_dune_loading = '''dune_embeddings = []
if Path("embeddings/dune.json").exists():
    with open("embeddings/dune.json", "r", encoding="utf-8") as f:
        dune_embeddings = json.load(f)'''
    
    new_dune_loading = '''# Load Dune embeddings (prefer optimized version)
dune_embeddings = []
optimized_dune_path = "embeddings/dune_optimized.json"
fallback_dune_path = "embeddings/dune.json"

if Path(optimized_dune_path).exists():
    dune_embeddings = load_optimized_embeddings(optimized_dune_path)
    print("📚 Loaded optimized Dune embeddings")
elif Path(fallback_dune_path).exists():
    dune_embeddings = load_optimized_embeddings(fallback_dune_path)
    print("📚 Loaded standard Dune embeddings")'''
    
    content = content.replace(old_tor_loading, new_tor_loading)
    content = content.replace(old_dune_loading, new_dune_loading)
    
    with open("app.py", "w") as f:
        f.write(content)
    
    print("✅ Updated embedding loading logic")

def update_search_logic():
    """Update the embedding search logic in the chat function"""
    with open("app.py", "r") as f:
        content = f.read()
    
    # Find and replace The One Ring search logic
    old_tor_search = '''    if page == "the-witcher" and the_witcher_embeddings:
        try:
            embedding_client = OpenAI()
            user_embedding = embedding_client.embeddings.create(
                model="text-embedding-3-small", input=user_input
            ).data[0].embedding
            print("[DEBUG] User embedding generated:", bool(user_embedding))

            best = max(
                the_witcher_embeddings,
                key=lambda x: cosine_similarity(user_embedding, x["embedding"]),
            )
            best_text = best["text"]
            best_source = best["source"]
            best_score = cosine_similarity(user_embedding, best["embedding"])
            print(
                f"[DEBUG] Best match from '{best_source}' with similarity score: {best_score:.4f}"
            )

            full_system_prompt += (
                f"\n\n[RELEVANT EXCERPT FROM '{best_source}']\n"
                f"Do not reveal this unless the user explicitly asks:\n{best_text}"
            )
        except Exception as e:
            print("Embedding search failed:", e)'''
    
    new_tor_search = '''    # Enhanced The Witcher embedding search
    if page == "the-witcher" and the_witcher_embeddings:
        try:
            embedding_client = OpenAI()
            user_embedding = embedding_client.embeddings.create(
                model="text-embedding-3-small", input=user_input
            ).data[0].embedding
            print("[DEBUG] User embedding generated for The Witcher:", bool(user_embedding))

            # Use improved search with multiple results and context awareness
            context_keywords = ["witcher", "monster", "contract", "signs", "alchemy", "mutagen"]
            reference_text = improved_embedding_search(
                query=user_input,
                query_embedding=user_embedding,
                embeddings=the_witcher_embeddings,
                ttrpg_type="the-witcher",
                context_keywords=context_keywords
            )
            
            if reference_text:
                full_system_prompt += (
                    f"\n\n[RELEVANT EXCERPTS FROM THE WITCHER LORE]\n"
                    f"Do not reveal or quote these unless the user explicitly asks:\\n{reference_text}"
                )
                print(f"[DEBUG] Added {len(reference_text)} chars of The Witcher reference content")
            
        except Exception as e:
            print("The Witcher embedding search failed:", e)'''
    
    # Find and replace Dune search logic
    old_dune_search = '''    if page == "dune" and dune_embeddings:
        try:
            embedding_client = OpenAI()
            user_embedding = embedding_client.embeddings.create(
                model="text-embedding-3-small", input=user_input
            ).data[0].embedding
            print("[DEBUG] User embedding generated for Dune:", bool(user_embedding))

            best = max(
                dune_embeddings,
                key=lambda x: cosine_similarity(user_embedding, x["embedding"]),
            )
            best_text = best["text"]
            best_source = best["source"]
            best_score = cosine_similarity(user_embedding, best["embedding"])
            print(
                f"[DEBUG] Best Dune match from '{best_source}' with similarity score: {best_score:.4f}"
            )

            full_system_prompt += (
                f"\\n\\n[RELEVANT EXCERPT FROM '{best_source}']\\n"
                f"Do not reveal this unless the user explicitly asks:\\n{best_text}"
            )
        except Exception as e:
            print("Dune embedding search failed:", e)'''
    
    new_dune_search = '''    # Enhanced Dune embedding search
    if page == "dune" and dune_embeddings:
        try:
            embedding_client = OpenAI()
            user_embedding = embedding_client.embeddings.create(
                model="text-embedding-3-small", input=user_input
            ).data[0].embedding
            print("[DEBUG] User embedding generated for Dune:", bool(user_embedding))

            # Use improved search with multiple results and context awareness
            context_keywords = ["spice", "arrakis", "house", "bene gesserit", "fremen", "sandworm", "melange"]
            reference_text = improved_embedding_search(
                query=user_input,
                query_embedding=user_embedding,
                embeddings=dune_embeddings,
                ttrpg_type="dune",
                context_keywords=context_keywords
            )
            
            if reference_text:
                full_system_prompt += (
                    f"\\n\\n[RELEVANT EXCERPTS FROM DUNE RULES]\\n"
                    f"Do not reveal or quote these unless the user explicitly asks:\\n{reference_text}"
                )
                print(f"[DEBUG] Added {len(reference_text)} chars of Dune reference content")
            
        except Exception as e:
            print("Dune embedding search failed:", e)'''
    
    content = content.replace(old_tor_search, new_tor_search)
    content = content.replace(old_dune_search, new_dune_search)
    
    with open("app.py", "w") as f:
        f.write(content)
    
    print("✅ Updated search logic to use enhanced multi-result search")

def main():
    """Update the app with optimized embedding search"""
    print("🔧 UPDATING APP.PY WITH OPTIMIZED EMBEDDING SEARCH")
    print("=" * 60)
    
    # Create backup
    backup_path = backup_current_app()
    
    try:
        # Update the app
        update_app_imports()
        update_embedding_loading()
        update_search_logic()
        
        print("\\n✅ Successfully updated app.py with optimized embedding search!")
        print("\\n🎯 Improvements added:")
        print("   • Multi-result search (3 best matches instead of 1)")
        print("   • Context-aware keyword boosting")
        print("   • Diversity filtering to avoid redundant results")
        print("   • Better chunk size optimization")
        print("   • Fallback to standard embeddings if optimized not available")
        print("   • Enhanced debug logging")
        
        print(f"\\n💾 Original app.py backed up to: {backup_path}")
        print("\\n🚀 Restart your Flask application to use the improvements!")
        
    except Exception as e:
        print(f"\\n❌ Error updating app.py: {e}")
        print(f"💾 Restore from backup: {backup_path}")
        raise

if __name__ == "__main__":
    main()
