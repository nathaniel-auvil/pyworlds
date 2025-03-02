import unittest
import os
import json
from ..models.save_manager import SaveManager
from ..models.game_state import GameState

class TestSaveManager(unittest.TestCase):
    def setUp(self):
        self.save_manager = SaveManager()
        self.game_state = GameState()
        self.test_save_file = "test_save.json"
    
    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.test_save_file):
            os.remove(self.test_save_file)
    
    def test_save_game(self):
        """Test saving game state"""
        # Save the game
        success = self.save_manager.save_game(self.game_state, self.test_save_file)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.test_save_file))
        
        # Verify file contents
        with open(self.test_save_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(data['corporation_name'], self.game_state.corporation_name)
            self.assertEqual(data['credits'], self.game_state.credits)
    
    def test_load_game(self):
        """Test loading game state"""
        # First save the game
        self.save_manager.save_game(self.game_state, self.test_save_file)
        
        # Modify the current game state
        self.game_state.credits = 5000
        self.game_state.corporation_name = "Changed Corp"
        
        # Load the saved game
        loaded_state = self.save_manager.load_game(self.test_save_file)
        
        # Verify loaded state
        self.assertEqual(loaded_state.corporation_name, "New Corporation")
        self.assertEqual(loaded_state.credits, 1000)
    
    def test_save_load_fleets(self):
        """Test saving and loading fleet data"""
        # Clear existing fleets and add a new one
        self.game_state.fleets = []
        fleet = self.game_state.add_fleet("Test Fleet")
        self.game_state.current_fleet_id = fleet.id
        
        # Save and load
        self.save_manager.save_game(self.game_state, self.test_save_file)
        loaded_state = self.save_manager.load_game(self.test_save_file)
        
        # Verify fleets
        self.assertEqual(len(loaded_state.fleets), len(self.game_state.fleets))
        self.assertEqual(loaded_state.fleets[0].name, "Test Fleet")
    
    def test_save_load_resources(self):
        """Test saving and loading resource data"""
        # Modify resources
        fleet = self.game_state.get_current_fleet()
        fleet.resources['metal'] = 500
        fleet.resources['gas'] = 300
        
        # Save and load
        self.save_manager.save_game(self.game_state, self.test_save_file)
        loaded_state = self.save_manager.load_game(self.test_save_file)
        
        # Verify resources
        loaded_fleet = loaded_state.get_current_fleet()
        self.assertEqual(loaded_fleet.resources['metal'], 500)
        self.assertEqual(loaded_fleet.resources['gas'], 300)
    
    def test_invalid_save_file(self):
        """Test loading invalid save file"""
        # Create invalid save file
        with open(self.test_save_file, 'w') as f:
            f.write("invalid json")
        
        # Try to load
        with self.assertRaises(Exception):
            self.save_manager.load_game(self.test_save_file)
    
    def test_nonexistent_save_file(self):
        """Test loading nonexistent save file"""
        with self.assertRaises(FileNotFoundError):
            self.save_manager.load_game("nonexistent.json")

if __name__ == '__main__':
    unittest.main() 