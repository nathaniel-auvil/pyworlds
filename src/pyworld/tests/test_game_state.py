import unittest
from ..models.game_state import GameState

class TestGameState(unittest.TestCase):
    def setUp(self):
        self.game_state = GameState()
    
    def test_initial_state(self):
        """Test initial game state"""
        self.assertEqual(self.game_state.corporation_name, "New Corporation")
        self.assertEqual(self.game_state.credits, 1000)
        self.assertEqual(len(self.game_state.fleets), 1)
        self.assertIsNotNone(self.game_state.get_current_fleet())
    
    def test_fleet_management(self):
        """Test fleet management functions"""
        # Test adding new fleet
        new_fleet = self.game_state.add_fleet("Test Fleet")
        self.assertEqual(len(self.game_state.fleets), 2)
        self.assertEqual(new_fleet.name, "Test Fleet")
        
        # Test setting current fleet
        self.assertTrue(self.game_state.set_current_fleet(new_fleet.id))
        self.assertEqual(self.game_state.get_current_fleet().id, new_fleet.id)
        
        # Test removing fleet
        self.assertTrue(self.game_state.remove_fleet(new_fleet.id))
        self.assertEqual(len(self.game_state.fleets), 1)
    
    def test_resource_costs(self):
        """Test resource cost calculations and deductions"""
        fleet = self.game_state.get_current_fleet()
        fleet.resources['metal'] = 1000
        fleet.resources['energy'] = 1000
        
        costs = {'credits': 500, 'metal': 200, 'energy': 100}
        
        # Test can_afford
        self.assertTrue(self.game_state.can_afford(costs))
        
        # Test deduct_resources
        self.assertTrue(self.game_state.deduct_resources(costs))
        self.assertEqual(self.game_state.credits, 500)
        self.assertEqual(fleet.resources['metal'], 800)
        self.assertEqual(fleet.resources['energy'], 900)
    
    def test_total_assets(self):
        """Test total assets calculation"""
        fleet = self.game_state.get_current_fleet()
        
        # Add some resources
        fleet.resources['metal'] = 1000  # Worth 10 each
        fleet.resources['gas'] = 500     # Worth 15 each
        fleet.mining_drones = 2          # Worth 500 each
        fleet.gas_collectors = 1         # Worth 750 each
        
        self.game_state.update_total_assets()
        
        expected_assets = (
            1000 +                  # Initial credits
            1000 +                  # Base ship value at level 1
            1000 * 10 +            # Metal value
            500 * 15 +             # Gas value
            2 * 500 +              # Drone value
            1 * 750                # Collector value
        )
        
        self.assertEqual(self.game_state.total_assets, expected_assets)
    
    def test_crew_and_power(self):
        """Test crew count and power usage properties"""
        fleet = self.game_state.get_current_fleet()
        fleet.mining_drones = 2
        fleet.gas_collectors = 1
        
        # Test crew count (sum of drones and collectors)
        self.assertEqual(self.game_state.crew, 3)
        
        # Test power usage
        expected_power_usage = (2 + 1) * 10  # Each drone/collector uses 10 power
        self.assertEqual(self.game_state.power_usage, expected_power_usage)

if __name__ == '__main__':
    unittest.main() 