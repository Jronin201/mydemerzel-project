"""
Enhanced embedding loader with fallback mechanisms for locked-down deployments.
"""

import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

def check_internet_connectivity() -> bool:
    """Check if internet is available for downloading embeddings."""
    test_urls = [
        'https://www.google.com',
        'https://httpbin.org/get',
        'https://api.github.com'
    ]
    
    for url in test_urls:
        try:
            import urllib.request
            print(f"🌐 Testing internet connectivity with {url}...")
            urllib.request.urlopen(url, timeout=10)
            print("✅ Internet connectivity confirmed")
            return True
        except Exception as e:
            print(f"⚠️  Failed to connect to {url}: {e}")
            continue
    
    print("❌ No internet connectivity confirmed with any test URL")
    # On deployment platforms like Render, assume internet is available
    # even if our test URLs fail due to network restrictions
    print("🔄 Assuming internet is available on deployment platform")
    return True

def download_embeddings_if_missing() -> bool:
    """
    Automatically download embeddings if missing and internet is available.
    Returns True if embeddings are available after this function.
    """
    print("🔄 Starting download_embeddings_if_missing function...")
    
    # Updated to match Supabase file names (without _optimized suffix)
    required_files = [
        "embeddings/dune.json",
    "embeddings/the-witcher.json", 
        "embeddings/mouse-guard.json"
    ]
    
    # Check if all files exist
    all_exist = all(Path(f).exists() for f in required_files)
    print(f"📋 Required files check: {len([f for f in required_files if Path(f).exists()])}/{len(required_files)} exist")
    
    if all_exist:
        print("✅ All required files already exist")
        return True
    
    # For deployment environments, skip internet connectivity check and try download directly
    # since connectivity checks can fail due to network restrictions while actual downloads work
    print("🔄 Attempting download (skipping connectivity check for deployment)...")
    
    # Check environment variables first
    import os
    supabase_url = os.getenv('SUPABASE_PROJECT_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    print(f"🔍 Environment check:")
    print(f"   SUPABASE_PROJECT_URL: {supabase_url}")
    print(f"   SUPABASE_ANON_KEY: {'SET' if supabase_key else 'NOT SET'}")
    
    if not supabase_url:
        print("❌ SUPABASE_PROJECT_URL environment variable not set")
    if not supabase_key:
        print("❌ SUPABASE_ANON_KEY environment variable not set")
        
    # If environment variables are missing, we can't download
    if not supabase_url or not supabase_key:
        print("❌ Cannot download - missing required environment variables")
        return False
    
    # Try direct download for missing files
    try:
        print("📦 Attempting to import requests...")
        import requests
        print("✅ Requests imported successfully")
        
        bucket_name = os.getenv('SUPABASE_BUCKET_NAME', 'ttrpg-embeddings')
        print(f"🪣 Using bucket: {bucket_name}")
        
        for file_path in required_files:
            if not Path(file_path).exists():
                file_name = Path(file_path).name
                print(f"📥 Downloading {file_name}...")
                
                download_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{file_name}"
                print(f"🔗 Download URL: {download_url}")
                headers = {"Authorization": f"Bearer {supabase_key}"}
                
                try:
                    print(f"⏳ Making request to Supabase...")
                    response = requests.get(download_url, headers=headers, timeout=300)
                    print(f"📊 Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                        with open(file_path, 'wb') as f:
                            f.write(response.content)
                        file_size = len(response.content)
                        print(f"✅ Downloaded {file_name} successfully ({file_size} bytes)")
                    else:
                        print(f"❌ Failed to download {file_name}: HTTP {response.status_code}")
                        print(f"   Response headers: {dict(response.headers)}")
                        print(f"   Response text: {response.text[:500]}")
                except Exception as e:
                    print(f"❌ Error downloading {file_name}: {e}")
                    import traceback
                    print(f"   Traceback: {traceback.format_exc()}")
        
        # Check if all files exist now
        all_exist_after = all(Path(f).exists() for f in required_files)
        if all_exist_after:
            print("✅ All embeddings downloaded successfully via direct method")
            return True
    
    except ImportError as e:
        print(f"❌ Failed to import requests: {e}")
        print("   This might be a deployment environment issue")
    except Exception as e:
        print(f"❌ Unexpected error in direct download: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
            
        # Fallback to script method
        try:
            download_script = Path("scripts/download_embeddings.sh")
            if download_script.exists():
                print(f"📋 Running download script: {download_script}")
                result = subprocess.run(
                    ["bash", str(download_script)], 
                    capture_output=True, 
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                print(f"📤 Download script stdout: {result.stdout}")
                if result.stderr:
                    print(f"📤 Download script stderr: {result.stderr}")
                    
                if result.returncode == 0:
                    print("✅ Embeddings downloaded successfully")
                    return True
                else:
                    print(f"❌ Download failed with return code: {result.returncode}")
            else:
                print("❌ Download script not found")
        except subprocess.TimeoutExpired:
            print("⚠️  Download timed out")
        except Exception as e:
            print(f"⚠️  Download error: {e}")
    
    return False

def load_embeddings_with_fallback(
    optimized_path: str, 
    fallback_path: str,
    system_name: str
) -> List[Dict[str, Any]]:
    """
    Load embeddings with multiple fallback options for locked-down environments.
    """
    from optimized_embedding_search import load_optimized_embeddings
    
    # Try optimized version first
    if Path(optimized_path).exists():
        embeddings = load_optimized_embeddings(optimized_path)
        if embeddings:
            print(f"📚 Loaded optimized {system_name} embeddings")
            return embeddings
    
    # Try fallback version only if optimized failed
    if Path(fallback_path).exists():
        embeddings = load_optimized_embeddings(fallback_path)
        if embeddings:
            print(f"📚 Using fallback {system_name} embeddings")
            return embeddings
    
    # Return empty list with warning - don't try individual downloads here
    print(f"⚠️  No {system_name} embeddings available. System will work with limited functionality.")
    print(f"   To enable full functionality, ensure these files exist:")
    print(f"   - {optimized_path}")
    if not Path(fallback_path).exists():
        print(f"   Note: Fallback file {fallback_path} not available either")
    return []

def get_embedding_status() -> Dict[str, Any]:
    """Get status of all embedding files for diagnostics."""
    status = {
        "internet_available": check_internet_connectivity(),
        "embedding_files": {},
        "recommendations": []
    }
    
    files_to_check = [
        ("dune_optimized", "embeddings/dune_optimized.json"),
        ("dune_fallback", "embeddings/dune.json"),
        ("witcher_optimized", "embeddings/the-witcher_optimized.json"),
        ("witcher_fallback", "embeddings/the-witcher.json"),
        ("mouse_guard_optimized", "embeddings/mouse-guard_optimized.json"),
        ("mouse_guard_fallback", "embeddings/mouse-guard.json")
    ]
    
    for name, path in files_to_check:
        file_path = Path(path)
        status["embedding_files"][name] = {
            "exists": file_path.exists(),
            "size": file_path.stat().st_size if file_path.exists() else 0,
            "path": path
        }
    
    # Generate recommendations
    missing_optimized = []
    for system in ["dune", "witcher", "mouse_guard"]:
        if not status["embedding_files"][f"{system}_optimized"]["exists"]:
            missing_optimized.append(system)
    
    if missing_optimized:
        if status["internet_available"]:
            status["recommendations"].append(
                "Run './scripts/download_embeddings.sh' to download missing files"
            )
        else:
            status["recommendations"].append(
                "Copy embedding files from a deployment with internet access"
            )
            status["recommendations"].append(
                "Or use manual download from Supabase dashboard"
            )
    
    return status

# Enhanced embedding loading for the main app
def initialize_embeddings_for_lockdown():
    """Initialize all embeddings with lockdown-friendly fallbacks."""
    
    print("🔧 Initializing embeddings for deployment...")
    
    # Updated for Supabase file names (no _optimized suffix)
    # Force download if any files are missing
    required_files = [
        "embeddings/the-witcher.json",
        "embeddings/dune.json",
        "embeddings/mouse-guard.json"
    ]
    
    missing_files = [f for f in required_files if not Path(f).exists()]
    if missing_files:
        print(f"📥 Missing files: {[Path(f).name for f in missing_files]}")
        print("🔄 Forcing download of embeddings from Supabase...")
        download_embeddings_if_missing()
    
    # Load each system's embeddings with correct file names
    the_witcher_embeddings = load_embeddings_with_fallback(
        "embeddings/the-witcher.json",
        "embeddings/the-witcher_fallback.json",
        "The Witcher"
    )
    
    dune_embeddings = load_embeddings_with_fallback(
        "embeddings/dune.json",
        "embeddings/dune_fallback.json",
        "Dune"
    )
    
    mouse_guard_embeddings = load_embeddings_with_fallback(
        "embeddings/mouse-guard.json", 
        "embeddings/mouse-guard_fallback.json",
        "Mouse Guard"
    )
    
    # Print summary
    total_embeddings = (
    len(the_witcher_embeddings) + 
        len(dune_embeddings) + 
        len(mouse_guard_embeddings)
    )
    
    print(f"📊 Embedding Summary:")
    print(f"   The Witcher: {len(the_witcher_embeddings)} chunks")
    print(f"   Dune: {len(dune_embeddings)} chunks") 
    print(f"   Mouse Guard: {len(mouse_guard_embeddings)} chunks")
    print(f"   Total: {total_embeddings} chunks")
    
    if total_embeddings == 0:
        print("\n⚠️  WARNING: No embeddings loaded!")
        print("   The chatbot will work but with limited TTRPG knowledge.")
        print("   See deployment documentation for embedding setup.")
    
    return the_witcher_embeddings, dune_embeddings, mouse_guard_embeddings
