from datetime import datetime, timedelta
from typing import Dict, Optional, List
from .universe import RegionVisibility

class Fleet:
    """Represents a fleet of ships"""
    
    def __init__(self, name: str = "Fleet"):
        self.id = id(self)  # Use object's memory address as ID
        self.name = name
        self.level = 1
        self.ship_type = "Explorer"
        self.mining_drones = 1
        self.gas_collectors = 1
        self._storage_capacity = 1000  # Base storage capacity
        self.resources = {
            'metal': 0,
            'gas': 0,
            'energy': 0
        }
        
        # Travel state
        self.current_region = None
        self.destination = None
        self.travel_start = None
        self.travel_end = None
        self.is_traveling = False
        
        # Probing state
        self.is_probing = False
        self.probe_start = None
        self.probe_end = None
        self.probe_region = None
    
    @property
    def storage_capacity(self) -> float:
        """Get the storage capacity, scaled by fleet level"""
        return self._storage_capacity * (1.0 + (self.level - 1) * 0.5)
    
    @property
    def storage_used(self) -> float:
        """Get the current storage used"""
        return sum(self.resources.values())
    
    @property
    def current_location(self) -> str:
        """Get the name of the current location"""
        if self.current_region:
            return self.current_region.name
        return "Unknown"
    
    def add_resource(self, resource_type: str, amount: float) -> float:
        """Add resources to the fleet's storage, returns the amount actually added"""
        if resource_type not in self.resources:
            self.resources[resource_type] = 0
            
        # Check storage capacity
        available_storage = self.storage_capacity - self.storage_used
        amount_to_add = min(amount, available_storage)
        
        # Add resources
        self.resources[resource_type] += amount_to_add
        
        return amount_to_add
    
    def get_resource_capacity(self, resource_type: str) -> float:
        """Get the capacity for a specific resource"""
        return self.storage_capacity
    
    def upgrade(self):
        """Upgrade the fleet to the next level"""
        self.level += 1
    
    def travel_to(self, destination, travel_hours: float = 1.0):
        """Start traveling to a destination"""
        if self.is_traveling:
            raise ValueError("Fleet is already traveling")
            
        if self.is_probing:
            raise ValueError("Fleet is currently probing a system")
            
        self.destination = destination
        self.travel_start = datetime.now()
        self.travel_end = self.travel_start + timedelta(hours=travel_hours)
        self.is_traveling = True
    
    def complete_travel(self):
        """Complete the travel, updating location"""
        if not self.is_traveling:
            return
            
        self.current_region = self.destination
        self.destination = None
        self.is_traveling = False
        self.travel_start = None
        self.travel_end = None
    
    def start_probing(self, region):
        """Start probing a region"""
        if self.is_traveling:
            raise ValueError("Fleet cannot probe while traveling")
            
        if self.is_probing:
            raise ValueError("Fleet is already probing")
            
        if region != self.current_region:
            raise ValueError("Fleet must be in the region to probe it")
            
        # Calculate probe time based on region level
        # Level 1 = 10 seconds, Level 2 = 20 seconds, etc.
        probe_hours = (10 * region.level) / 3600  # Convert seconds to hours
        
        self.is_probing = True
        self.probe_region = region
        self.probe_start = datetime.now()
        self.probe_end = self.probe_start + timedelta(hours=probe_hours)
    
    def complete_probing(self):
        """Complete the probing process"""
        if not self.is_probing:
            return False
            
        if datetime.now() < self.probe_end:
            return False  # Not done yet
            
        # Mark the region as probed and discover resources
        if self.probe_region:
            self.probe_region.visibility = RegionVisibility.EXPLORED
            self.probe_region.discover_deposits()
            
            # Calculate extraction time estimates
            extraction_times = {}
            for deposit in self.probe_region.deposits:
                # Base extraction time is 1 hour per 1000 units
                base_time = deposit.amount / 1000
                # Higher level systems take longer to extract from
                extraction_times[deposit.resource_type] = base_time * (1 + (self.probe_region.level - 1) * 0.5)
        
        # Reset probing state
        self.is_probing = False
        self.probe_region = None
        self.probe_start = None
        self.probe_end = None
        
        return True
    
    def get_travel_progress(self) -> float:
        """Get the progress of current travel (0-1)"""
        if not self.is_traveling:
            return 0.0
            
        now = datetime.now()
        if now >= self.travel_end:
            return 1.0
            
        total_time = (self.travel_end - self.travel_start).total_seconds()
        elapsed_time = (now - self.travel_start).total_seconds()
        
        return min(1.0, elapsed_time / total_time)
    
    def get_probe_progress(self) -> float:
        """Get the progress of current probing (0-1)"""
        if not self.is_probing:
            return 0.0
            
        now = datetime.now()
        if now >= self.probe_end:
            return 1.0
            
        total_time = (self.probe_end - self.probe_start).total_seconds()
        elapsed_time = (now - self.probe_start).total_seconds()
        
        return min(1.0, elapsed_time / total_time)
    
    def update(self, dt: float):
        """Update the fleet state"""
        # Check if travel is complete
        if self.is_traveling and datetime.now() >= self.travel_end:
            self.complete_travel()
            
        # Check if probing is complete
        if self.is_probing and datetime.now() >= self.probe_end:
            self.complete_probing()

    def to_dict(self):
        """Convert the fleet data to a dictionary for serialization."""
        return {
            'name': self.name,
            'level': self.level,
            'ship_type': self.ship_type,
            'current_location': self.current_location,
            'resources': self.resources,
            'storage': {'capacity': self.storage_capacity},
            'travel': {
                'is_traveling': self.is_traveling,
                'current_region': self.current_region,
                'destination': self.destination,
                'travel_start': self.travel_start,
                'travel_end': self.travel_end
            },
            'probing': {
                'is_probing': self.is_probing,
                'probe_region': self.probe_region,
                'probe_start': self.probe_start,
                'probe_end': self.probe_end
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Fleet':
        fleet = cls(data['name'])
        fleet.level = data['level']
        fleet.ship_type = data['ship_type']
        fleet.current_region = data['travel']['current_region']
        fleet.destination = data['travel']['destination']
        fleet.travel_start = data['travel']['travel_start']
        fleet.travel_end = data['travel']['travel_end']
        fleet.is_traveling = data['travel']['is_traveling']
        fleet.probe_region = data['probing']['probe_region']
        fleet.probe_start = data['probing']['probe_start']
        fleet.probe_end = data['probing']['probe_end']
        fleet.is_probing = data['probing']['is_probing']
        fleet.resources = data['resources']
        fleet._storage_capacity = data['storage']['capacity']
        return fleet 