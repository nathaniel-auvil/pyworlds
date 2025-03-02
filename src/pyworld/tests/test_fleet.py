import unittest
from datetime import datetime, timedelta
from ..models.fleet import Fleet

class TestFleet(unittest.TestCase):
    def setUp(self):
        self.fleet = Fleet("Test Fleet")
    
    def test_initial_state(self):
        """Test initial fleet state"""
        self.assertEqual(self.fleet.name, "Test Fleet")
        self.assertEqual(self.fleet.ship_type, "Freighter")
        self.assertEqual(self.fleet.current_location, "Home System")
        self.assertEqual(self.fleet.level, 1)
        self.assertEqual(self.fleet.mining_drones, 1)
        self.assertEqual(self.fleet.gas_collectors, 0)
        self.assertEqual(self.fleet.storage_capacity, 1000)
    
    def test_resource_management(self):
        """Test resource addition and removal"""
        # Test adding resources
        added = self.fleet.add_resource('metal', 500)
        self.assertEqual(added, 500)
        self.assertEqual(self.fleet.resources['metal'], 500)
        
        # Test storage limit
        added = self.fleet.add_resource('metal', 600)
        self.assertEqual(added, 500)  # Only 500 more should fit
        self.assertEqual(self.fleet.resources['metal'], 1000)
        
        # Test removing resources
        removed = self.fleet.remove_resource('metal', 300)
        self.assertEqual(removed, 300)
        self.assertEqual(self.fleet.resources['metal'], 700)
    
    def test_power_management(self):
        """Test power generation and usage"""
        # Base power generation at level 1
        self.assertEqual(self.fleet.power_generation, 100)
        
        # Power usage with default equipment
        self.assertEqual(self.fleet.power_usage, 10)  # 1 mining drone * 10
        
        # Available power
        self.assertEqual(self.fleet.available_power, 90)
    
    def test_upgrade_process(self):
        """Test fleet upgrade process"""
        # Start upgrade
        self.assertTrue(self.fleet.start_upgrade())
        self.assertIsNotNone(self.fleet.upgrade_start)
        self.assertIsNotNone(self.fleet.upgrade_end)
        
        # Complete upgrade
        self.fleet.upgrade_end = datetime.now() - timedelta(seconds=1)
        self.fleet.update(0.1)  # Trigger update to complete upgrade
        
        self.assertEqual(self.fleet.level, 2)
        self.assertEqual(self.fleet.max_drones, 4)  # 2 + level
        self.assertEqual(self.fleet.max_collectors, 2)  # 1 + level//2
    
    def test_travel_system(self):
        """Test fleet travel system"""
        # Start travel
        destination = "Alpha Centauri"
        self.assertTrue(self.fleet.start_travel(destination, 2.0))
        self.assertTrue(self.fleet.is_traveling)
        self.assertEqual(self.fleet.destination, destination)
        
        # Complete travel
        self.fleet.travel_end = datetime.now() - timedelta(seconds=1)
        self.fleet.update(0.1)  # Trigger update to complete travel
        
        self.assertEqual(self.fleet.current_location, destination)
        self.assertFalse(self.fleet.is_traveling)
    
    def test_resource_collection(self):
        """Test automatic resource collection"""
        # Test collection rates over 1 hour
        dt = 3600  # 1 hour in seconds
        
        # Reset energy to ensure consistent test
        self.fleet.resources['energy'] = 100
        
        # Update for one hour
        self.fleet.update(dt)
        
        # Check metal collection (10 per drone per hour)
        self.assertAlmostEqual(self.fleet.resources['metal'], 10)
        
        # Check gas collection (no collectors initially)
        self.assertAlmostEqual(self.fleet.resources['gas'], 0)
        
        # Check energy regeneration (5 per hour)
        expected_energy = min(self.fleet.max_energy, 100 + 5)  # Initial + 5/hour, capped at max
        self.assertAlmostEqual(self.fleet.resources['energy'], expected_energy)

if __name__ == '__main__':
    unittest.main() 