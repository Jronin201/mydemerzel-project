#!/usr/bin/env python3
"""
Test script for persistent character information functionality
"""

import sys
import os
import unittest
from pathlib import Path

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from user_character_info import (
    save_user_character_info,
    load_user_character_info,
    get_user_character_sessions,
    delete_user_character_info
)


class TestCharacterInfoPersistence(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.test_username = "test_user"
        self.test_ttrpg = "dune"
        
    def tearDown(self):
        """Clean up test data"""
        # Clean up any test files
        delete_user_character_info(self.test_username, self.test_ttrpg)
        delete_user_character_info(self.test_username, "the-one-ring")
        
        # Remove test directory if empty
        test_dir = Path("character_info") / self.test_username
        if test_dir.exists() and not any(test_dir.iterdir()):
            test_dir.rmdir()
            
    def test_save_and_load_character_info(self):
        """Test saving and loading character information"""
        character_name = "Paul Atreides"
        character_stats = "Duke's son, prescient abilities, skilled fighter"
        
        # Save character info
        success = save_user_character_info(
            self.test_username, 
            self.test_ttrpg, 
            character_name, 
            character_stats
        )
        self.assertTrue(success)
        
        # Load character info
        loaded_info = load_user_character_info(self.test_username, self.test_ttrpg)
        
        self.assertEqual(loaded_info["character_name"], character_name)
        self.assertEqual(loaded_info["character_stats"], character_stats)
        self.assertNotEqual(loaded_info["last_updated"], "Never")
        
    def test_multiple_ttrpg_persistence(self):
        """Test that different TTRPGs maintain separate character info"""
        # Save character info for Dune
        dune_character = "Paul Atreides"
        dune_stats = "Fremen leader"
        save_user_character_info(self.test_username, "dune", dune_character, dune_stats)
        
    # Save character info for The Witcher
        ring_character = "Frodo Baggins"
        ring_stats = "Hobbit with the Ring"
        save_user_character_info(self.test_username, "the-one-ring", ring_character, ring_stats)
        
        # Load and verify both are separate
        dune_info = load_user_character_info(self.test_username, "dune")
        ring_info = load_user_character_info(self.test_username, "the-one-ring")
        
        self.assertEqual(dune_info["character_name"], dune_character)
        self.assertEqual(dune_info["character_stats"], dune_stats)
        
        self.assertEqual(ring_info["character_name"], ring_character)
        self.assertEqual(ring_info["character_stats"], ring_stats)
        
        # Verify they're different
        self.assertNotEqual(dune_info["character_name"], ring_info["character_name"])
        
    def test_empty_character_info(self):
        """Test handling of empty character information"""
        # Load non-existent character info
        loaded_info = load_user_character_info(self.test_username, "nonexistent")
        
        self.assertEqual(loaded_info["character_name"], "")
        self.assertEqual(loaded_info["character_stats"], "")
        self.assertEqual(loaded_info["last_updated"], "Never")
        
    def test_character_sessions(self):
        """Test getting all character sessions for a user"""
        # Save character info for multiple TTRPGs
        save_user_character_info(self.test_username, "dune", "Paul", "Duke")
        save_user_character_info(self.test_username, "the-one-ring", "Frodo", "Hobbit")
        
        # Get all sessions
        sessions = get_user_character_sessions(self.test_username)
        
        self.assertEqual(len(sessions), 2)
        ttrpg_systems = [session["ttrpg_system"] for session in sessions]
        self.assertIn("dune", ttrpg_systems)
        self.assertIn("the-one-ring", ttrpg_systems)
        
    def test_update_existing_character_info(self):
        """Test updating existing character information"""
        # Save initial character info
        initial_name = "Paul Atreides"
        initial_stats = "Young duke"
        save_user_character_info(self.test_username, self.test_ttrpg, initial_name, initial_stats)
        
        # Update character info
        updated_name = "Paul Muad'Dib"
        updated_stats = "Fremen leader, Emperor slayer"
        save_user_character_info(self.test_username, self.test_ttrpg, updated_name, updated_stats)
        
        # Load and verify update
        loaded_info = load_user_character_info(self.test_username, self.test_ttrpg)
        
        self.assertEqual(loaded_info["character_name"], updated_name)
        self.assertEqual(loaded_info["character_stats"], updated_stats)


if __name__ == "__main__":
    print("Testing character information persistence...")
    unittest.main()
