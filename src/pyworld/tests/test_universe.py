import unittest
from ..models.universe import Universe, Region, ResourceDeposit, ResourceGrant
from datetime import timedelta

class TestUniverse(unittest.TestCase):
    def setUp(self):
        self.universe = Universe()
    
    def test_initial_state(self):
        """Test initial universe state"""
        self.assertGreater(len(self.universe.regions), 0)
        self.assertIsNotNone(self.universe.home_region)
    
    def test_get_connected_regions(self):
        """Test getting connected regions"""
        home = self.universe.home_region
        connected = self.universe.get_connected_regions(home)
        self.assertIsInstance(connected, list)
        self.assertTrue(all(isinstance(r, Region) for r in connected))
    
    def test_get_regions_by_level(self):
        """Test getting regions by level range"""
        regions = self.universe.get_regions_by_level(1, 3)
        self.assertTrue(all(1 <= r.level <= 3 for r in regions))
    
    def test_get_regions_by_distance(self):
        """Test getting regions within distance"""
        home = self.universe.home_region
        regions = self.universe.get_regions_by_distance(home, 2.0)
        self.assertTrue(all(isinstance(r, Region) for r in regions))
    
    def test_get_path_between(self):
        """Test finding path between regions"""
        home = self.universe.home_region
        target = next(iter(self.universe.regions.values()))
        if target != home:
            path = self.universe.get_path_between(home, target)
            self.assertIsInstance(path, list)
            if path:
                self.assertEqual(path[0], home)
                self.assertEqual(path[-1], target)

class TestRegion(unittest.TestCase):
    def setUp(self):
        self.region = Region("Test Region", 1, (0, 0))
    
    def test_initial_state(self):
        """Test initial region state"""
        self.assertEqual(self.region.name, "Test Region")
        self.assertEqual(self.region.level, 1)
        self.assertEqual(self.region.position, (0, 0))
        self.assertEqual(len(self.region.deposits), 0)
        self.assertEqual(len(self.region.grants), 0)
    
    def test_add_deposit(self):
        """Test adding resource deposit"""
        deposit = ResourceDeposit("metal", 100, 1.0)
        self.region.deposits.append(deposit)
        self.assertEqual(len(self.region.deposits), 1)
        self.assertEqual(self.region.deposits[0], deposit)
    
    def test_get_discovered_deposits(self):
        """Test getting discovered deposits"""
        deposit1 = ResourceDeposit("metal", 100, 1.0)
        deposit2 = ResourceDeposit("gas", 100, 1.0)
        deposit2.discovered = True
        self.region.deposits.extend([deposit1, deposit2])
        
        discovered = self.region.get_discovered_deposits()
        self.assertEqual(len(discovered), 1)
        self.assertEqual(discovered[0], deposit2)
    
    def test_get_active_grants(self):
        """Test getting active grants"""
        deposit = ResourceDeposit("metal", 100, 1.0)
        grant = ResourceGrant(deposit, "Test Corp", 3600)
        self.region.grants.append(grant)
        
        active = self.region.get_active_grants()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0], grant)

class TestResourceDeposit(unittest.TestCase):
    def setUp(self):
        self.deposit = ResourceDeposit("metal", 100, 1.5)
    
    def test_initial_state(self):
        """Test initial deposit state"""
        self.assertEqual(self.deposit.resource_type, "metal")
        self.assertEqual(self.deposit.base_amount, 100)
        self.assertEqual(self.deposit.quality, 1.5)
        self.assertFalse(self.deposit.discovered)
    
    def test_collection_rate(self):
        """Test collection rate calculation"""
        # Base rate at collector level 1
        self.assertEqual(self.deposit.collection_rate(1), 150)  # 100 * 1.5 * 1.0
        
        # Rate with higher collector level
        self.assertAlmostEqual(
            self.deposit.collection_rate(2),
            165,  # 100 * 1.5 * 1.1
            places=2
        )
    
    def test_display_name(self):
        """Test display name formatting"""
        expected = "Metal Deposit (Quality: 1.5)"
        self.assertEqual(self.deposit.display_name, expected)
    
    def test_base_collection_rate(self):
        """Test base collection rate"""
        self.assertEqual(self.deposit.base_collection_rate, 150)  # 100 * 1.5

class TestResourceGrant(unittest.TestCase):
    def setUp(self):
        self.deposit = ResourceDeposit("metal", 100, 1.5)
        self.grant = ResourceGrant(self.deposit, "Test Corp", 3600)
    
    def test_initial_state(self):
        """Test initial grant state"""
        self.assertEqual(self.grant.deposit, self.deposit)
        self.assertEqual(self.grant.corporation, "Test Corp")
        self.assertEqual(self.grant.duration, timedelta(seconds=3600))
    
    def test_time_remaining(self):
        """Test time remaining calculation"""
        self.assertLessEqual(self.grant.time_remaining.total_seconds(), 3600)
        self.assertGreaterEqual(self.grant.time_remaining.total_seconds(), 0)
    
    def test_expired(self):
        """Test expiration check"""
        self.assertFalse(self.grant.expired)
        
        # Force expiration
        self.grant.start_time = self.grant.start_time - timedelta(seconds=3601)
        self.assertTrue(self.grant.expired)
    
    def test_display_name(self):
        """Test display name formatting"""
        expected = "Metal Deposit (Quality: 1.5) - Test Corp"
        self.assertEqual(self.grant.display_name, expected)
    
    def test_progress(self):
        """Test progress calculation"""
        self.assertGreaterEqual(self.grant.progress, 0)
        self.assertLessEqual(self.grant.progress, 1)

if __name__ == '__main__':
    unittest.main() 