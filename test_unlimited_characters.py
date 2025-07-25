#!/usr/bin/env python3
"""
Test script to verify unlimited character support in the textboxes
"""
import sys
import os
import json
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from user_character_info import (
    save_user_character_info,
    load_user_character_info
)

def test_unlimited_characters():
    """Test that the system can handle very large amounts of text"""
    print("🧪 Testing Unlimited Character Support")
    print("=" * 50)
    
    test_user = "unlimited_test"
    test_ttrpg = "stress_test"
    
    # Create very long text content (simulating extensive notes)
    base_text = "This is a test of the unlimited character system. " * 20
    character_blocks = []
    notes_blocks = []
    
    # Create progressively larger blocks of text
    for i in range(1, 6):
        multiplier = 100 * i
        char_block = f"Character Section {i}: " + (base_text * multiplier)
        notes_block = f"Notes Section {i}: " + (base_text * multiplier) 
        character_blocks.append(char_block)
        notes_blocks.append(notes_block)
    
    mega_character_info = "\n\n".join(character_blocks)
    mega_notes = "\n\n".join(notes_blocks)
    
    print(f"📏 Mega Character Info: {len(mega_character_info):,} characters")
    print(f"📏 Mega Notes: {len(mega_notes):,} characters")
    print(f"📏 Total: {len(mega_character_info) + len(mega_notes):,} characters")
    
    # Test saving very large content
    print("\n🔄 Saving mega content...")
    success = save_user_character_info(
        test_user, test_ttrpg, mega_character_info, mega_notes, "user"
    )
    print(f"✅ Save successful: {success}")
    
    # Test loading very large content
    print("\n🔄 Loading mega content...")
    loaded = load_user_character_info(test_user, test_ttrpg)
    
    loaded_char_len = len(loaded.get('character_name', ''))
    loaded_notes_len = len(loaded.get('character_stats', ''))
    
    print(f"📥 Loaded Character Info: {loaded_char_len:,} characters")
    print(f"📥 Loaded Notes: {loaded_notes_len:,} characters")
    
    # Verify integrity
    char_match = loaded.get('character_name', '') == mega_character_info
    notes_match = loaded.get('character_stats', '') == mega_notes
    
    print(f"\n✅ Character integrity: {char_match}")
    print(f"✅ Notes integrity: {notes_match}")
    
    if char_match and notes_match:
        print("🎉 SUCCESS: Unlimited character system working perfectly!")
        print(f"🚀 Successfully handled {len(mega_character_info) + len(mega_notes):,} characters!")
    else:
        print("❌ FAILURE: Content mismatch detected")
        if not char_match:
            print(f"   Character expected: {len(mega_character_info)} chars, got: {loaded_char_len} chars")
        if not notes_match:
            print(f"   Notes expected: {len(mega_notes)} chars, got: {loaded_notes_len} chars")
    
    # Test file size
    char_file = Path("character_info") / test_user / f"{test_ttrpg}_character.json"
    if char_file.exists():
        file_size = char_file.stat().st_size
        print(f"\n💾 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        # Test if we can actually read the JSON
        try:
            with open(char_file, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            print("✅ JSON file structure is valid")
        except Exception as e:
            print(f"❌ JSON parsing error: {e}")
    
    return char_match and notes_match

if __name__ == "__main__":
    success = test_unlimited_characters()
    print("\n" + "=" * 50)
    if success:
        print("🎊 ALL TESTS PASSED: Unlimited character system is working!")
        exit(0)
    else:
        print("💥 TESTS FAILED: Issues detected with unlimited character system")
        exit(1)
