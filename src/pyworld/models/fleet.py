from datetime import datetime, timedelta
from typing import Dict, Optional

class Fleet:
    def __init__(self, name: str, ship_type: str = "Freighter"):
        self.id = id(self)  # Unique identifier
        self.name = name
        self.ship_type = ship_type
        self.current_location = "Home System"
        
        # Resources
        self.resources = {
            'metal': 0,
            'gas': 0,
            'energy': 100,  # Start with full energy
            'refined_metal': 0,
            'refined_gas': 0
        }
        
        # Ship capabilities
        self.level = 1
        self.mining_drones = 1  # Start with one mining drone
        self.gas_collectors = 0
        self.storage_capacity = 1000
        self.max_drones = 2
        self.max_collectors = 1
        self.max_energy = 100
        
        # Upgrade status
        self.upgrade_start: Optional[datetime] = None
        self.upgrade_end: Optional[datetime] = None
        
        # Movement
        self.is_traveling = False
        self.travel_start: Optional[datetime] = None
        self.travel_end: Optional[datetime] = None
        self.destination: Optional[str] = None
    
    @property
    def storage_used(self) -> int:
        """Calculate total storage used by resources"""
        return sum(amount for resource, amount in self.resources.items()
                  if resource != 'energy')
    
    @property
    def storage_available(self) -> int:
        """Calculate remaining storage capacity"""
        return self.storage_capacity - self.storage_used
    
    def get_resource_capacity(self, resource: str) -> int:
        """Get the capacity for a specific resource"""
        if resource == 'energy':
            return self.max_energy
        return self.storage_capacity
    
    def can_add_resource(self, resource: str, amount: int) -> bool:
        """Check if the specified amount of resource can be added"""
        if resource == 'energy':
            return self.resources['energy'] + amount <= self.max_energy
        return self.storage_used + amount <= self.storage_capacity
    
    def add_resource(self, resource: str, amount: int) -> int:
        """Add resource and return amount actually added"""
        if resource == 'energy':
            space = self.max_energy - self.resources['energy']
            added = min(amount, space)
            self.resources['energy'] += added
            return added
        
        space = self.storage_capacity - self.storage_used
        added = min(amount, space)
        self.resources[resource] = self.resources.get(resource, 0) + added
        return added
    
    def remove_resource(self, resource: str, amount: int) -> int:
        """Remove resource and return amount actually removed"""
        available = self.resources.get(resource, 0)
        removed = min(amount, available)
        self.resources[resource] = available - removed
        return removed
    
    def start_upgrade(self):
        """Start upgrading the ship"""
        if self.upgrade_start is not None:
            return False
        
        self.upgrade_start = datetime.now()
        # Base upgrade time is 5 minutes, increases with level
        upgrade_time = timedelta(minutes=5 * (1.2 ** (self.level - 1)))
        self.upgrade_end = self.upgrade_start + upgrade_time
        return True
    
    def complete_upgrade(self):
        """Complete the ship upgrade"""
        if not self.upgrade_start or not self.upgrade_end:
            return False
        
        self.level += 1
        
        # Increase capabilities with level
        self.max_drones = 2 + self.level
        self.max_collectors = 1 + self.level // 2
        self.storage_capacity = 1000 * (1.5 ** (self.level - 1))
        self.max_energy = 100 * (1.2 ** (self.level - 1))
        
        # Reset upgrade status
        self.upgrade_start = None
        self.upgrade_end = None
        return True
    
    def start_travel(self, destination: str, distance: float):
        """Start traveling to a new location"""
        if self.is_traveling:
            return False
        
        self.is_traveling = True
        self.destination = destination
        self.travel_start = datetime.now()
        
        # Base travel time is 1 minute per unit of distance
        travel_time = timedelta(minutes=distance)
        self.travel_end = self.travel_start + travel_time
        return True
    
    def complete_travel(self):
        """Complete the travel to new location"""
        if not self.is_traveling or not self.destination:
            return False
        
        self.current_location = self.destination
        self.is_traveling = False
        self.destination = None
        self.travel_start = None
        self.travel_end = None
        return True
    
    def update(self, dt: float):
        """Update the fleet state"""
        # Check for upgrade completion
        if (self.upgrade_start and self.upgrade_end and 
            datetime.now() >= self.upgrade_end):
            self.complete_upgrade()
        
        # Check for travel completion
        if (self.is_traveling and self.travel_end and 
            datetime.now() >= self.travel_end):
            self.complete_travel()
        
        # Update resource collection
        if not self.is_traveling:
            # Mining drones collect metal
            metal_rate = 10 * self.mining_drones * dt / 3600  # per hour
            self.add_resource('metal', metal_rate)
            
            # Gas collectors collect gas
            gas_rate = 8 * self.gas_collectors * dt / 3600  # per hour
            self.add_resource('gas', gas_rate)
            
            # Energy regeneration (5 per hour)
            energy_rate = 5 * dt / 3600  # per hour
            current_energy = self.resources.get('energy', 0)
            self.resources['energy'] = min(
                self.max_energy,
                current_energy + energy_rate
            )
    
    @property
    def power_generation(self) -> float:
        """Calculate total power generation"""
        # Base power generation plus level bonus
        return 100 * (1.2 ** (self.level - 1))
    
    @property
    def power_usage(self) -> float:
        """Calculate total power usage"""
        # Each drone and collector uses 10 energy
        return (self.mining_drones + self.gas_collectors) * 10
    
    @property
    def available_power(self) -> float:
        """Calculate available power"""
        return self.power_generation - self.power_usage 

    def to_dict(self):
        """Convert the fleet data to a dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'ship_type': self.ship_type,
            'current_location': self.current_location,
            'resources': self.resources,
            'storage': {'capacity': self.storage_capacity},
            'level': self.level
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Fleet':
        fleet = cls(data['name'], data['ship_type'])
        fleet.id = data['id']
        fleet.current_location = data['current_location']
        fleet.resources = data['resources']
        fleet.storage_capacity = data['storage']['capacity']
        fleet.level = data['level']
        return fleet 