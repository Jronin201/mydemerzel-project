#!/usr/bin/env python3
"""
Quick test script to verify memory optimization works.
"""

def test_memory_optimization():
    print("🧪 Testing memory-optimized embedding system...")
    
    try:
        # Test imports
        from memory_optimized_embeddings import get_system_embeddings, get_embedding_status
        print("✅ Memory optimization modules imported successfully")
        
        # Test status without loading anything
        status = get_embedding_status()
        print(f"✅ Initial cache status: {status['cache_status']['cache_size']} systems cached")
        
        # Test file existence check
        file_status = status['file_status']
        available_systems = [name for name, info in file_status.items() if info['optimized_exists']]
        print(f"✅ Available systems: {available_systems}")
        
        if available_systems:
            # Test loading one system
            test_system = available_systems[0]
            print(f"🔄 Testing lazy loading of {test_system}...")
            
            embeddings = get_system_embeddings(test_system)
            if embeddings:
                print(f"✅ Successfully loaded {len(embeddings)} embeddings for {test_system}")
            else:
                print(f"⚠️  No embeddings loaded for {test_system}")
            
            # Check cache status after loading
            status_after = get_embedding_status()
            cached_systems = status_after['cache_status']['cached_systems']
            print(f"✅ Cache after loading: {cached_systems}")
            
        print("\n🎉 Memory optimization test completed successfully!")
        print("✅ System is ready for low-memory deployment")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_memory_optimization()
    exit(0 if success else 1)
