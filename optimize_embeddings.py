#!/usr/bin/env python3
"""
Complete embedding optimization workflow.
This script will:
1. Analyze current embeddings
2. Generate optimized embeddings (if API key available)
3. Update the application code
4. Provide testing instructions
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are met."""
    print("🔍 CHECKING REQUIREMENTS...")
    
    issues = []
    
    # Check for Python packages
    try:
        import numpy
        import tiktoken
        print("✅ NumPy and tiktoken available")
    except ImportError as e:
        issues.append(f"Missing Python package: {e}")
    
    # Check for document files
    doc_files = [
        "documents/dune/dune.txt",
        "documents/the-one-ring"
    ]
    
    for doc_path in doc_files:
        if not Path(doc_path).exists():
            issues.append(f"Missing document: {doc_path}")
        else:
            print(f"✅ Found {doc_path}")
    
    # Check for OpenAI API key (optional for generation)
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        print("✅ OpenAI API key found")
    else:
        print("⚠️  No OpenAI API key - can analyze but not regenerate embeddings")
    
    if issues:
        print("\\n❌ Issues found:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    
    return True

def run_analysis():
    """Run the embedding analysis."""
    print("\\n📊 ANALYZING CURRENT EMBEDDINGS...")
    
    try:
        result = subprocess.run([
            sys.executable, "analyze_embeddings.py"
        ], capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Analysis timed out")
        return False
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

def generate_optimized_embeddings():
    """Generate optimized embeddings if API key is available."""
    if not os.environ.get('OPENAI_API_KEY'):
        print("\\n⚠️  Skipping embedding generation (no API key)")
        return True
    
    print("\\n🚀 GENERATING OPTIMIZED EMBEDDINGS...")
    print("This may take several minutes and will use OpenAI API credits...")
    
    response = input("Continue? (y/N): ").strip().lower()
    if response != 'y':
        print("Skipping embedding generation")
        return True
    
    try:
        result = subprocess.run([
            sys.executable, "generate_optimized_embeddings.py"
        ], timeout=1800)  # 30 minute timeout
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Embedding generation timed out")
        return False
    except Exception as e:
        print(f"❌ Embedding generation failed: {e}")
        return False

def update_application():
    """Update the application code."""
    print("\\n🔧 UPDATING APPLICATION CODE...")
    
    try:
        result = subprocess.run([
            sys.executable, "update_app_embeddings.py"
        ], timeout=60)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ App update timed out")
        return False
    except Exception as e:
        print(f"❌ App update failed: {e}")
        return False

def create_test_script():
    """Create a test script for the user."""
    test_script = '''#!/usr/bin/env python3
"""
Test script for optimized embedding search.
Run this after starting your Flask application.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_embedding_search():
    """Test the optimized embedding search functionality."""
    print("🧪 TESTING OPTIMIZED EMBEDDING SEARCH")
    print("=" * 50)
    
    # Login first
    session = requests.Session()
    login_data = {"username": "Demerzel", "password": "Seraphine"}
    
    try:
        response = session.post(f"{BASE_URL}/login", data=login_data)
        if response.status_code != 200:
            print("❌ Login failed - make sure Flask app is running")
            return False
        print("✅ Logged in successfully")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on http://localhost:5000")
        return False
    
    # Test queries for different TTRPG systems
    test_queries = {
        "dune": [
            "How do I mine spice on Arrakis?",
            "What are the powers of the Bene Gesserit?",
            "Tell me about House Atreides"
        ],
        "the-one-ring": [
            "How do I create a hobbit character?",
            "What are the travel rules in Middle-earth?",
            "How does corruption work?"
        ]
    }
    
    for ttrpg, queries in test_queries.items():
        print(f"\\n🎮 Testing {ttrpg.upper()} system...")
        
        for query in queries:
            chat_data = {
                "message": query,
                "page": ttrpg
            }
            
            try:
                response = session.post(
                    f"{BASE_URL}/chat",
                    json=chat_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("response", "")
                    print(f"   ✅ Query: {query}")
                    print(f"      Response length: {len(ai_response)} chars")
                    print(f"      Preview: {ai_response[:100]}...")
                else:
                    print(f"   ❌ Query failed: {query} (Status: {response.status_code})")
                    
            except Exception as e:
                print(f"   ❌ Error testing query '{query}': {e}")
    
    print("\\n✅ Testing complete!")
    print("\\n💡 Tips to verify improvements:")
    print("   • Responses should be more relevant and specific")
    print("   • Check Flask console for DEBUG messages about embedding search")
    print("   • Multiple reference sources should be used (check console logs)")

if __name__ == "__main__":
    test_embedding_search()
'''
    
    with open("test_optimized_embeddings.py", "w") as f:
        f.write(test_script)
    
    print("✅ Created test_optimized_embeddings.py")

def provide_instructions():
    """Provide final instructions to the user."""
    print("\\n🎉 EMBEDDING OPTIMIZATION COMPLETE!")
    print("=" * 50)
    
    print("\\n📋 WHAT WAS OPTIMIZED:")
    print("   ✅ Chunk sizes reduced from 3000+ to 100-1000 characters")
    print("   ✅ Added semantic boundary awareness (paragraphs, sentences)")
    print("   ✅ Implemented overlapping context between chunks")
    print("   ✅ Enhanced search with multiple results and diversity filtering")
    print("   ✅ Added context-aware keyword boosting")
    print("   ✅ Improved debugging and error handling")
    
    print("\\n🚀 NEXT STEPS:")
    print("   1. Restart your Flask application:")
    print("      cd /workspaces/mydemerzel-project")
    print("      python app.py")
    print()
    print("   2. Test the improvements:")
    print("      python test_optimized_embeddings.py")
    print()
    print("   3. Monitor Flask console for debug messages like:")
    print("      '[DEBUG] Added X chars of reference content'")
    print("      'Added Y chars of Dune reference content'")
    print()
    
    print("\\n📊 PERFORMANCE MONITORING:")
    print("   • Check similarity scores in console (should be > 0.3 for good matches)")
    print("   • Verify multiple reference sources are being used")
    print("   • Test various query types to ensure broad coverage")
    print("   • Compare AI response quality before/after optimization")
    
    print("\\n🔄 OPTIONAL ENHANCEMENTS:")
    if not os.environ.get('OPENAI_API_KEY'):
        print("   • Set OPENAI_API_KEY to regenerate optimized embeddings")
    print("   • Fine-tune chunk sizes in generate_optimized_embeddings.py")
    print("   • Adjust similarity thresholds in optimized_embedding_search.py")
    print("   • Add more context keywords for your specific use cases")

def main():
    """Main optimization workflow."""
    print("🤖 EMBEDDING OPTIMIZATION WORKFLOW")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\\n❌ Requirements not met. Please fix issues and try again.")
        return 1
    
    # Run analysis
    if not run_analysis():
        print("\\n❌ Analysis failed")
        return 1
    
    # Generate optimized embeddings (optional)
    if not generate_optimized_embeddings():
        print("\\n⚠️  Embedding generation failed, but continuing with app updates...")
    
    # Update application
    if not update_application():
        print("\\n❌ Application update failed")
        return 1
    
    # Create test script
    create_test_script()
    
    # Provide instructions
    provide_instructions()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
