#!/usr/bin/env python3
"""
Integration test for character information persistence in the web app
"""

import sys
import os
import unittest
import json
import tempfile
from pathlib import Path

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from user_character_info import save_user_character_info, load_user_character_info, delete_user_character_info


class TestCharacterInfoIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.test_username = "test_user"
        
        # Create a test session with logged-in user
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_username
            sess['logged_in'] = True
            
    def tearDown(self):
        """Clean up test data"""
        # Clean up any test files
        test_systems = ["dune", "the-one-ring", "call-of-cthulhu", "general"]
        for system in test_systems:
            delete_user_character_info(self.test_username, system)
        
        # Remove test directory if empty
        test_dir = Path("character_info") / self.test_username
        if test_dir.exists() and not any(test_dir.iterdir()):
            test_dir.rmdir()
    
    def login_user(self):
        """Mock user login for testing"""
        return self.client.post('/login', data={
            'username': 'Demerzel',
            'password': 'Seraphine'
        }, follow_redirects=True)
    
    def test_character_info_api_get_empty(self):
        """Test getting character info when none exists"""
        # Mock login
        self.login_user()
        
        # Clear any existing character data for clean test
        clear_data = {
            "ttrpg": "dune",
            "character_name": "",
            "character_stats": ""
        }
        self.client.post('/api/character-info', 
                        data=json.dumps(clear_data),
                        content_type='application/json')
        
        response = self.client.get('/api/character-info?ttrpg=dune')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['character_name'], "")
        self.assertEqual(data['character_stats'], "")
        self.assertEqual(data['ttrpg_system'], "dune")
    
    def test_character_info_api_save_and_load(self):
        """Test saving and loading character info via API"""
        # Mock login
        self.login_user()
        
        # Save character info via API
        character_data = {
            "ttrpg": "dune",
            "character_name": "Paul Atreides",
            "character_stats": "Duke's son, prescient abilities"
        }
        
        response = self.client.post('/api/character-info', 
                                  data=json.dumps(character_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Load character info via API
        response = self.client.get('/api/character-info?ttrpg=dune')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['character_name'], character_data['character_name'])
        self.assertEqual(data['character_stats'], character_data['character_stats'])
        self.assertEqual(data['ttrpg_system'], "dune")
    
    def test_multiple_ttrpg_separation(self):
        """Test that different TTRPGs maintain separate character info"""
        # Mock login
        self.login_user()
        
        # Save character info for Dune
        dune_data = {
            "ttrpg": "dune",
            "character_name": "Paul Atreides",
            "character_stats": "Fremen leader"
        }
        self.client.post('/api/character-info', 
                        data=json.dumps(dune_data),
                        content_type='application/json')
        
    # Save character info for The Witcher
        ring_data = {
            "ttrpg": "the-one-ring",
            "character_name": "Frodo Baggins", 
            "character_stats": "Hobbit with the Ring"
        }
        self.client.post('/api/character-info',
                        data=json.dumps(ring_data),
                        content_type='application/json')
        
        # Load Dune character info
        response = self.client.get('/api/character-info?ttrpg=dune')
        dune_result = json.loads(response.data)
        
    # Load The Witcher character info
        response = self.client.get('/api/character-info?ttrpg=the-one-ring')
        ring_result = json.loads(response.data)
        
        # Verify they're separate
        self.assertEqual(dune_result['character_name'], "Paul Atreides")
        self.assertEqual(ring_result['character_name'], "Frodo Baggins")
        self.assertNotEqual(dune_result['character_name'], ring_result['character_name'])
    
    def test_character_sessions_api(self):
        """Test getting all character sessions for a user"""
        # Mock login
        self.login_user()
        
        # Clear any existing data first
        existing_response = self.client.get('/api/character-sessions')
        if existing_response.status_code == 200:
            existing_data = json.loads(existing_response.data)
            for session in existing_data.get('sessions', []):
                clear_data = {
                    "ttrpg": session['ttrpg_system'],
                    "character_name": "",
                    "character_stats": ""
                }
                self.client.post('/api/character-info',
                               data=json.dumps(clear_data),
                               content_type='application/json')
        
        # Save character info for multiple TTRPGs
        ttprgs = [
            {"ttrpg": "dune", "character_name": "Paul", "character_stats": "Duke"},
            {"ttrpg": "the-one-ring", "character_name": "Frodo", "character_stats": "Hobbit"},
            {"ttrpg": "call-of-cthulhu", "character_name": "Detective", "character_stats": "Investigator"}
        ]
        
        for ttrpg_data in ttprgs:
            self.client.post('/api/character-info',
                           data=json.dumps(ttrpg_data),
                           content_type='application/json')
        
        # Get all character sessions
        response = self.client.get('/api/character-sessions')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        # We should have at least the 3 we created, but there might be empty ones from previous tests
        self.assertGreaterEqual(len(data['sessions']), 3)
        
        # Verify all TTRPGs we created are present (filter out empty sessions)
        active_sessions = [session for session in data['sessions'] 
                         if session.get('character_name') and session.get('character_name').strip()]
        active_systems = [session['ttrpg_system'] for session in active_sessions]
        self.assertIn('dune', active_systems)
        self.assertIn('the-one-ring', active_systems)
        self.assertIn('call-of-cthulhu', active_systems)
    
    def test_character_info_update(self):
        """Test updating existing character information"""
        # Mock login
        self.login_user()
        
        # Save initial character info
        initial_data = {
            "ttrpg": "dune",
            "character_name": "Paul Atreides",
            "character_stats": "Young duke"
        }
        self.client.post('/api/character-info',
                        data=json.dumps(initial_data),
                        content_type='application/json')
        
        # Update character info
        updated_data = {
            "ttrpg": "dune",
            "character_name": "Paul Muad'Dib",
            "character_stats": "Fremen leader, Emperor slayer"
        }
        response = self.client.post('/api/character-info',
                                   data=json.dumps(updated_data),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Load and verify update
        response = self.client.get('/api/character-info?ttrpg=dune')
        data = json.loads(response.data)
        
        self.assertEqual(data['character_name'], "Paul Muad'Dib")
        self.assertEqual(data['character_stats'], "Fremen leader, Emperor slayer")


if __name__ == "__main__":
    print("Testing character information persistence integration...")
    unittest.main()
