#!/usr/bin/env python3
"""
Test script to verify TTRPG-specific system prompts are working correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import load_system_prompt

def test_system_prompts():
    """Test that system prompts are loaded correctly for each TTRPG."""
    
    print("Testing TTRPG-specific system prompt loading...")
    print("=" * 60)
    
    # Test global prompt loading
    global_prompt = load_system_prompt("")
    print(f"✓ Global prompt loaded: {len(global_prompt)} characters")
    print(f"Global prompt preview: {global_prompt[:100]}...")
    print()
    
    # Test each TTRPG system
    ttrpgs = ["dune", "the-witcher", "zweihander"]
    
    for ttrpg in ttrpgs:
        print(f"Testing {ttrpg}:")
        prompt = load_system_prompt(ttrpg)
        
        # Check that prompt is longer than global (indicates TTRPG-specific content was added)
        if len(prompt) > len(global_prompt):
            print(f"  ✓ TTRPG-specific prompt loaded: {len(prompt)} characters")
            
            # Check for TTRPG-specific keywords
            keywords = {
                "dune": ["Dune", "spice", "Atreides", "Game Master"],
                "the-witcher": ["Witcher", "mutagen", "signs", "monster"],
                "zweihander": ["Plain", "Gothic", "investigator", "mystery"]
            }
            
            found_keywords = []
            for keyword in keywords[ttrpg]:
                if keyword in prompt:
                    found_keywords.append(keyword)
            
            if found_keywords:
                print(f"  ✓ Contains expected keywords: {', '.join(found_keywords)}")
            else:
                print(f"  ⚠ Missing expected keywords: {', '.join(keywords[ttrpg])}")
                
            # Show a preview of the TTRPG-specific content
            ttrpg_specific = prompt[len(global_prompt):].strip()
            if ttrpg_specific:
                print(f"  ✓ TTRPG-specific content preview: {ttrpg_specific[:100]}...")
            
        else:
            print(f"  ✗ No TTRPG-specific content found (same length as global)")
        
        print()
    
    print("System prompt test completed!")
    return True

if __name__ == "__main__":
    test_system_prompts()
