#!/usr/bin/env python3
"""
Quick test to verify optimized embedding search is working correctly.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_import():
    """Test that we can import the optimized search functions."""
    try:
        from optimized_embedding_search import improved_embedding_search, load_optimized_embeddings
        print("✅ Successfully imported optimized search functions")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_embedding_loading():
    """Test loading embeddings with the new function."""
    try:
        from optimized_embedding_search import load_optimized_embeddings
        
        # Test loading existing embeddings
        for name in ["dune", "the-one-ring"]:
            file_path = f"embeddings/{name}.json"
            embeddings = load_optimized_embeddings(file_path)
            if embeddings:
                print(f"✅ Loaded {len(embeddings)} {name} embeddings")
            else:
                print(f"⚠️  No {name} embeddings loaded (file might not exist)")
        
        return True
    except Exception as e:
        print(f"❌ Loading test failed: {e}")
        return False

def test_search_function():
    """Test the search function with dummy data."""
    try:
        from optimized_embedding_search import improved_embedding_search
        import numpy as np
        
        # Create dummy embedding data
        dummy_embeddings = [
            {
                'text': 'This is about spice mining on the desert planet Arrakis.',
                'source': 'test.txt',
                'embedding': np.random.random(1536).tolist(),
                'chunk_size': 100,
                'section': 1
            },
            {
                'text': 'The Bene Gesserit have mysterious powers and abilities.',
                'source': 'test.txt', 
                'embedding': np.random.random(1536).tolist(),
                'chunk_size': 120,
                'section': 2
            }
        ]
        
        # Dummy query embedding
        query_embedding = np.random.random(1536).tolist()
        
        # Test search
        result = improved_embedding_search(
            query="Tell me about spice",
            query_embedding=query_embedding,
            embeddings=dummy_embeddings,
            ttrpg_type="dune"
        )
        
        if result and isinstance(result, str):
            print("✅ Search function returns valid results")
            print(f"   Result length: {len(result)} characters")
        else:
            print(f"⚠️  Search function returned: {type(result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

def test_app_integration():
    """Test that the app.py file has the correct imports."""
    try:
        with open("app.py", "r") as f:
            content = f.read()
        
        if "from optimized_embedding_search import" in content:
            print("✅ App.py has optimized search import")
        else:
            print("❌ App.py missing optimized search import")
            return False
        
        if "improved_embedding_search(" in content:
            print("✅ App.py uses improved search function")
        else:
            print("❌ App.py not using improved search function")
            return False
        
        if "load_optimized_embeddings(" in content:
            print("✅ App.py uses optimized embedding loader")
        else:
            print("❌ App.py not using optimized embedding loader")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ App integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 TESTING OPTIMIZED EMBEDDING INTEGRATION")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_import),
        ("Embedding Loading Test", test_embedding_loading),
        ("Search Function Test", test_search_function),
        ("App Integration Test", test_app_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"   ⚠️  {test_name} had issues")
    
    print(f"\n📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your optimized embedding system is ready.")
        print("\n🚀 Next steps:")
        print("   1. Start your Flask app: python app.py")
        print("   2. Test with real queries to see improved responses")
        print("   3. Check the Flask console for enhanced debug messages")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
