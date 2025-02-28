import unittest
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = str(Path(__file__).parent.parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from pyworld.models.ship import Module, ResourceCollector, StorageModule, ProductionModule, Ship, Mothership

class TestModule(unittest.TestCase):
    def setUp(self):
        self.module = Module("Test Module", "test")
    
    def test_id_generation(self):
        """Test that module IDs are generated correctly"""
        self.assertEqual(self.module.id, "test_module")
        
    def test_power_usage(self):
        """Test power usage calculation"""
        base_power = self.module.power_usage()
        self.module.level = 2
        self.assertAlmostEqual(self.module.power_usage(), base_power * 1.1)
        
    def test_crew_required(self):
        """Test crew requirement calculation"""
        base_crew = self.module.crew_required()
        self.module.level = 2
        self.assertEqual(self.module.crew_required(), max(1, int(base_crew * 1.1)))
        
    def test_upgrade_lifecycle(self):
        """Test the full upgrade lifecycle"""
        # Start upgrade
        self.assertTrue(self.module.start_upgrade())
        self.assertIsNotNone(self.module.upgrade_start)
        self.assertIsNotNone(self.module.upgrade_end)
        
        # Try starting another upgrade while one is in progress
        self.assertFalse(self.module.start_upgrade())
        
        # Check completion before time
        self.assertFalse(self.module.complete_upgrade())
        
        # Simulate time passing
        self.module.upgrade_end = datetime.now() - timedelta(seconds=1)
        
        # Check completion after time
        self.assertTrue(self.module.complete_upgrade())
        self.assertEqual(self.module.level, 2)
        self.assertIsNone(self.module.upgrade_start)
        self.assertIsNone(self.module.upgrade_end)

class TestResourceCollector(unittest.TestCase):
    def setUp(self):
        self.collector = ResourceCollector("Mining Drones", "metal", 10.0)
    
    def test_collection_rate(self):
        """Test collection rate calculation"""
        base_rate = self.collector.collection_rate()
        self.collector.level = 2
        self.assertAlmostEqual(self.collector.collection_rate(), base_rate * 1.25)

class TestStorageModule(unittest.TestCase):
    def setUp(self):
        self.storage = StorageModule("Cargo Hold", "general", 1000)
    
    def test_capacity(self):
        """Test storage capacity calculation"""
        base_capacity = self.storage.capacity()
        self.storage.level = 2
        self.assertEqual(self.storage.capacity(), base_capacity * 2)

class TestProductionModule(unittest.TestCase):
    def setUp(self):
        self.production = ProductionModule("Factory", "drones", 1.0)
    
    def test_production_rate(self):
        """Test production rate calculation"""
        base_rate = self.production.production_rate()
        self.production.level = 2
        self.assertAlmostEqual(self.production.production_rate(), base_rate * 1.2)

class TestShip(unittest.TestCase):
    def setUp(self):
        self.ship = Ship("Test Ship")
        self.ship.modules = {
            'storage': StorageModule("Cargo Hold", "general", 1000),
            'collector': ResourceCollector("Mining Drones", "metal", 10.0)
        }
        self.ship.current_crew = 10
        self.ship.power_generation = 100
    
    def test_available_power(self):
        """Test available power calculation"""
        used_power = sum(m.power_usage() for m in self.ship.modules.values())
        self.assertAlmostEqual(self.ship.available_power, self.ship.power_generation - used_power)
    
    def test_available_crew(self):
        """Test available crew calculation"""
        assigned_crew = sum(m.crew_required() for m in self.ship.modules.values())
        self.assertEqual(self.ship.available_crew, self.ship.current_crew - assigned_crew)
    
    def test_resource_capacity(self):
        """Test resource capacity calculation"""
        capacity = self.ship.get_resource_capacity("metal")
        self.assertEqual(capacity, self.ship.modules['storage'].capacity())

class TestMothership(unittest.TestCase):
    def setUp(self):
        self.mothership = Mothership()
    
    def test_initialization(self):
        """Test mothership initialization"""
        self.assertIn('mining_drones', self.mothership.modules)
        self.assertIn('gas_collector', self.mothership.modules)
        self.assertIn('power_core', self.mothership.modules)
        self.assertIn('cargo_hold', self.mothership.modules)
        self.assertIn('crew_quarters', self.mothership.modules)
        self.assertIn('drone_factory', self.mothership.modules)
    
    def test_crew_property(self):
        """Test crew property"""
        self.assertEqual(self.mothership.crew, self.mothership.current_crew)
        self.mothership.current_crew = 30
        self.assertEqual(self.mothership.crew, 30)
    
    def test_power_usage(self):
        """Test power usage calculation"""
        # Calculate expected power usage from all active modules
        expected_power = sum(
            module.power_usage() for module in self.mothership.modules.values()
            if module.is_active
        )
        self.assertEqual(self.mothership.power_usage, expected_power)
        
        # Test with a module deactivated
        module = next(iter(self.mothership.modules.values()))
        module.is_active = False
        expected_power = sum(
            module.power_usage() for module in self.mothership.modules.values()
            if module.is_active
        )
        self.assertEqual(self.mothership.power_usage, expected_power)
    
    def test_resource_update(self):
        """Test resource update over time"""
        initial_metal = self.mothership.resources['metal']
        
        # Simulate 1 hour passing
        self.mothership.update_resources(3600, game_speed=1.0)
        
        # Check that resources increased
        self.assertGreater(self.mothership.resources['metal'], initial_metal)
        
    def test_total_resource_value(self):
        """Test calculation of total resource value"""
        # Reset all resources to 0
        self.mothership.resources = {
            'metal': 0,
            'gas': 0,
            'energy': 0,
            'refined_metal': 0,
            'refined_gas': 0,
            'fuel': 0,
            'last_update': self.mothership.resources['last_update']
        }
        
        # Set test resource values
        self.mothership.resources.update({
            'metal': 100,
            'gas': 50,
            'refined_metal': 20,
            'refined_gas': 10
        })
        
        # Define expected value based on default resource prices
        expected_value = (
            100 * 1 +  # metal at 1 credit each
            50 * 2 +   # gas at 2 credits each
            20 * 5 +   # refined_metal at 5 credits each
            10 * 10    # refined_gas at 10 credits each
        )
        
        self.assertEqual(self.mothership.total_resource_value(), expected_value)

def run_tests():
    """Run the tests from command line"""
    unittest.main(verbosity=2)

if __name__ == '__main__':
    run_tests() 