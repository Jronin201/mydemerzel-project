#!/usr/bin/env python3
"""
Test Mouse Guard embedding download from Supabase
"""
import os
import requests
from pathlib import Path

def test_supabase_connection():
    """Test if we can connect to Supabase and download Mouse Guard embeddings"""
    
    # Get environment variables
    supabase_url = os.getenv('SUPABASE_PROJECT_URL', 'https://npsuzfgqaykewpndhhmb.supabase.co')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    bucket_name = os.getenv('SUPABASE_BUCKET_NAME', 'ttrpg-embeddings')
    
    print(f"🔗 Testing connection to: {supabase_url}")
    print(f"🪣 Bucket: {bucket_name}")
    print(f"🔑 Key set: {'Yes' if supabase_key else 'No'}")
    
    if not supabase_key:
        print("❌ SUPABASE_ANON_KEY not set!")
        return False
    
    # Test downloading Mouse Guard embeddings
    file_name = "mouse-guard_optimized.json"
    download_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{file_name}"
    
    print(f"\n📥 Testing download from: {download_url}")
    
    try:
        headers = {"Authorization": f"Bearer {supabase_key}"}
        response = requests.head(download_url, headers=headers, timeout=30)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            content_length = response.headers.get('content-length')
            print(f"✅ Mouse Guard embeddings found! Size: {content_length} bytes")
            return True
        else:
            print(f"❌ Failed to access file. Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_download_mouse_guard():
    """Test actually downloading the Mouse Guard file"""
    
    supabase_url = os.getenv('SUPABASE_PROJECT_URL', 'https://npsuzfgqaykewpndhhmb.supabase.co')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    bucket_name = os.getenv('SUPABASE_BUCKET_NAME', 'ttrpg-embeddings')
    
    if not supabase_key:
        print("❌ Cannot test download - SUPABASE_ANON_KEY not set")
        return False
    
    file_name = "mouse-guard_optimized.json"
    download_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{file_name}"
    output_path = Path("test_download_mouse_guard.json")
    
    print(f"\n📥 Downloading to: {output_path}")
    
    try:
        headers = {"Authorization": f"Bearer {supabase_key}"}
        response = requests.get(download_url, headers=headers, timeout=300)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            file_size = output_path.stat().st_size
            print(f"✅ Downloaded successfully! Size: {file_size} bytes")
            
            # Clean up
            output_path.unlink()
            return True
        else:
            print(f"❌ Download failed. Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Download error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Mouse Guard Supabase Download")
    print("=" * 50)
    
    connection_ok = test_supabase_connection()
    
    if connection_ok:
        print("\n" + "=" * 50)
        download_ok = test_download_mouse_guard()
        
        if download_ok:
            print("\n🎉 All tests passed! Mouse Guard download should work.")
        else:
            print("\n❌ Download test failed!")
    else:
        print("\n❌ Connection test failed!")
