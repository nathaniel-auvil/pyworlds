import unittest
from ..models.station import SpaceStation

class TestSpaceStation(unittest.TestCase):
    def setUp(self):
        self.station = SpaceStation()
    
    def test_initial_state(self):
        """Test initial station state"""
        self.assertEqual(self.station.level, 1)
        self.assertEqual(len(self.station.modules), 0)
        self.assertEqual(self.station.max_modules, 3)  # Base max modules
    
    def test_add_module(self):
        """Test adding a module"""
        result = self.station.add_module("refinery")
        self.assertTrue(result)
        self.assertEqual(len(self.station.modules), 1)
        self.assertIn("refinery", [m.type for m in self.station.modules])
    
    def test_max_modules_limit(self):
        """Test module limit enforcement"""
        # Add modules up to limit
        for _ in range(self.station.max_modules):
            self.assertTrue(self.station.add_module("refinery"))
        
        # Try to add one more
        self.assertFalse(self.station.add_module("refinery"))
        self.assertEqual(len(self.station.modules), self.station.max_modules)
    
    def test_upgrade_station(self):
        """Test station upgrade"""
        initial_max = self.station.max_modules
        self.station.upgrade()
        self.assertEqual(self.station.level, 2)
        self.assertGreater(self.station.max_modules, initial_max)
    
    def test_process_resources(self):
        """Test resource processing"""
        # Add refinery module
        self.station.add_module("refinery")
        
        # Test processing
        input_resources = {
            'metal': 100,
            'gas': 100
        }
        output = self.station.process_resources(input_resources)
        
        self.assertGreater(output.get('refined_metal', 0), 0)
        self.assertGreater(output.get('refined_gas', 0), 0)
    
    def test_get_module_by_type(self):
        """Test getting module by type"""
        self.station.add_module("refinery")
        module = self.station.get_module_by_type("refinery")
        self.assertIsNotNone(module)
        self.assertEqual(module.type, "refinery")
    
    def test_remove_module(self):
        """Test removing a module"""
        self.station.add_module("refinery")
        result = self.station.remove_module("refinery")
        self.assertTrue(result)
        self.assertEqual(len(self.station.modules), 0)
    
    def test_upgrade_module(self):
        """Test upgrading a module"""
        self.station.add_module("refinery")
        module = self.station.get_module_by_type("refinery")
        initial_level = module.level
        
        self.station.upgrade_module("refinery")
        self.assertEqual(module.level, initial_level + 1)
    
    def test_processing_efficiency(self):
        """Test processing efficiency calculations"""
        self.station.add_module("refinery")
        module = self.station.get_module_by_type("refinery")
        
        # Base efficiency at level 1
        base_efficiency = module.efficiency
        
        # Upgrade and check improved efficiency
        module.upgrade()
        self.assertGreater(module.efficiency, base_efficiency)

if __name__ == '__main__':
    unittest.main() 