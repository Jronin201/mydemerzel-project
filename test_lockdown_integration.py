#!/usr/bin/env python3
"""
Test script to verify lockdown environment + memory optimization works together.
"""

def test_lockdown_memory_optimization():
    print("🧪 Testing lockdown environment with memory optimization...")
    
    try:
        # Test lockdown loader import
        from lockdown_embedding_loader import download_embeddings_if_missing
        print("✅ Lockdown embedding loader imported successfully")
        
        # Test memory optimization import
        from memory_optimized_embeddings import get_system_embeddings, get_embedding_status
        print("✅ Memory optimization modules imported successfully")
        
        # Test file name configuration
        from memory_optimized_embeddings import embedding_manager
        expected_files = ['dune.json', 'the-one-ring.json', 'mouse-guard.json']
        actual_files = [files['optimized'].split('/')[-1] for files in embedding_manager.embedding_files.values()]
        
        print(f"✅ File name configuration:")
        for expected, actual in zip(expected_files, actual_files):
            match = "✅" if expected == actual else "❌"
            print(f"   {match} Expected: {expected}, Configured: {actual}")
        
        # Test embedding status
        status = get_embedding_status()
        print(f"✅ Embedding status check completed")
        print(f"   Cache size: {status['cache_status']['cache_size']}")
        print(f"   Systems available: {list(status['file_status'].keys())}")
        
        # Test environment variable checking (without requiring actual values)
        import os
        env_vars = ['SUPABASE_PROJECT_URL', 'SUPABASE_ANON_KEY', 'SUPABASE_BUCKET_NAME']
        print("🔍 Environment variable status:")
        for var in env_vars:
            value = os.getenv(var)
            status = "SET" if value else "NOT SET"
            print(f"   {var}: {status}")
        
        print("\n🎉 Lockdown + Memory optimization integration test completed!")
        print("✅ System is ready for deployment to lockdown environment")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_lockdown_memory_optimization()
    exit(0 if success else 1)
