import unittest
from datetime import datetime, timedelta
from ..models.buildings import Building

class TestBuilding(unittest.TestCase):
    def setUp(self):
        self.building = Building(
            name="Test Building",
            level=1,
            base_production=10,
            base_capacity=1000,
            cost={'metal': 100, 'crystal': 50},
            build_time=60
        )
    
    def test_initial_state(self):
        """Test initial building state"""
        self.assertEqual(self.building.level, 1)
        self.assertEqual(self.building.base_production, 10)
        self.assertEqual(self.building.base_capacity, 1000)
        self.assertEqual(self.building.base_build_time, 60)
        self.assertIsNone(self.building.current_build)
    
    def test_calculate_production(self):
        """Test production calculation"""
        # Level 1 production
        self.assertEqual(self.building.calculate_production(), 10)
        
        # Level 2 production (25% increase)
        self.building.level = 2
        self.assertEqual(self.building.calculate_production(), 12.5)
    
    def test_calculate_capacity(self):
        """Test capacity calculation"""
        # Level 1 capacity
        self.assertEqual(self.building.calculate_capacity(), 1000)
        
        # Level 2 capacity
        self.building.level = 2
        self.assertEqual(self.building.calculate_capacity(), 2000)
    
    def test_calculate_cost(self):
        """Test upgrade cost calculation"""
        # Level 1 to 2 cost
        costs = self.building.calculate_cost()
        self.assertEqual(costs['metal'], 150)  # 100 * 1.5
        self.assertEqual(costs['crystal'], 75)  # 50 * 1.5
        
        # Level 2 to 3 cost
        self.building.level = 2
        costs = self.building.calculate_cost()
        self.assertEqual(costs['metal'], 225)  # 150 * 1.5
        self.assertEqual(costs['crystal'], 112)  # 75 * 1.5
    
    def test_calculate_build_time(self):
        """Test build time calculation"""
        # Level 1 build time
        self.assertEqual(self.building.calculate_build_time(), 60)
        
        # Level 2 build time (20% increase)
        self.building.level = 2
        self.assertEqual(self.building.calculate_build_time(), 72)
    
    def test_building_without_production(self):
        """Test building without production capability"""
        building = Building(name="No Production Building", level=1, cost={'metal': 100})
        self.assertEqual(building.calculate_production(), 0)
    
    def test_building_without_capacity(self):
        """Test building without storage capacity"""
        building = Building(name="No Capacity Building", level=1, cost={'metal': 100})
        self.assertEqual(building.calculate_capacity(), 0)

if __name__ == '__main__':
    unittest.main() 