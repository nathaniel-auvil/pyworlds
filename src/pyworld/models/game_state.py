from datetime import datetime, timedelta
from typing import List, Optional
from .ship import Mothership
from .station import SpaceStation
from .universe import Universe
from .fleet import Fleet

class Building:
    def __init__(self, level, base_production=None, base_capacity=None, cost=None, build_time=60):
        self.level = level
        self.base_production = base_production
        self.base_capacity = base_capacity
        self.base_cost = cost or {'metal': 100, 'crystal': 50}
        self.base_build_time = build_time
        self.current_build = None
        
    def calculate_production(self):
        if self.base_production is None:
            return 0
        return self.base_production * (1.25 ** (self.level - 1))
    
    def calculate_capacity(self):
        if self.base_capacity is None:
            return 0
        return self.base_capacity * self.level
    
    def calculate_cost(self):
        return {
            resource: int(amount * (1.5 ** self.level))
            for resource, amount in self.base_cost.items()
        }
    
    def calculate_build_time(self):
        return self.base_build_time * (1.2 ** self.level)

class GameState:
    def __init__(self):
        self.corporation_name = "New Corporation"
        self.credits = 1000
        self.total_assets = self.credits
        
        # Initialize universe
        self.universe = Universe()
        self.current_region = self.universe.home_region
        
        # Initialize station
        self.station = SpaceStation()
        
        # Initialize fleets with a starting freighter
        self.fleets: List[Fleet] = []
        self.current_fleet_id: Optional[int] = None
        self.add_starting_fleet()
        
        # Game state
        self.is_traveling = False
        self.travel_progress = 0.0
        self.travel_destination = None
        self.travel_eta = None
        
        # Initialize resources
        self.resources = {
            'metal': 500,
            'crystal': 300,
            'energy': 100,
            'last_update': datetime.now().timestamp()
        }
        
        # Initialize storage
        self.storage = {
            'metal': 1000,
            'crystal': 1000
        }
        
        # Initialize buildings
        self.buildings = {
            'metal_mine': Building(
                level=1,
                base_production=10,
                cost={'metal': 60, 'crystal': 15},
                build_time=60
            ),
            'crystal_mine': Building(
                level=1,
                base_production=8,
                cost={'metal': 48, 'crystal': 24},
                build_time=80
            ),
            'solar_plant': Building(
                level=1,
                base_production=20,
                cost={'metal': 75, 'crystal': 30},
                build_time=100
            ),
            'storage_facility': Building(
                level=1,
                base_capacity=1000,
                cost={'metal': 100, 'crystal': 50},
                build_time=120
            ),
            'shipyard': Building(
                level=0,
                cost={'metal': 400, 'crystal': 200},
                build_time=300
            ),
            'research_lab': Building(
                level=0,
                cost={'metal': 200, 'crystal': 400},
                build_time=240
            )
        }
        
        self.game_speed = 1.0  # Default game speed
    
    def add_starting_fleet(self):
        """Add the starting freighter fleet"""
        fleet = Fleet("Fleet Alpha")
        self.fleets.append(fleet)
        self.current_fleet_id = fleet.id
    
    def get_current_fleet(self) -> Optional[Fleet]:
        """Get the currently selected fleet"""
        if self.current_fleet_id is None:
            return None
        return next(
            (f for f in self.fleets if f.id == self.current_fleet_id),
            None
        )
    
    def set_current_fleet(self, fleet_id: int) -> bool:
        """Set the current fleet by ID"""
        if any(f.id == fleet_id for f in self.fleets):
            self.current_fleet_id = fleet_id
            return True
        return False
    
    def add_fleet(self, name: str, ship_type: str = "Freighter") -> Fleet:
        """Add a new fleet"""
        fleet = Fleet(name, ship_type)
        self.fleets.append(fleet)
        return fleet
    
    def remove_fleet(self, fleet_id: int) -> bool:
        """Remove a fleet by ID"""
        fleet = next((f for f in self.fleets if f.id == fleet_id), None)
        if fleet:
            self.fleets.remove(fleet)
            if self.current_fleet_id == fleet_id:
                self.current_fleet_id = self.fleets[0].id if self.fleets else None
            return True
        return False
    
    def update(self, dt: float):
        """Update game state"""
        # Update all fleets
        for fleet in self.fleets:
            fleet.update(dt)
        
        # Update total assets
        self.update_total_assets()
    
    def update_total_assets(self):
        """Calculate total assets including fleet values and resources"""
        total = self.credits
        
        # Add value of each fleet
        for fleet in self.fleets:
            # Base ship value
            ship_value = 1000 * (1.5 ** (fleet.level - 1))
            
            # Add value of drones and collectors
            drone_value = 500 * fleet.mining_drones
            collector_value = 750 * fleet.gas_collectors
            
            # Add value of resources
            resource_values = {
                'metal': 10,
                'gas': 15,
                'refined_metal': 25,
                'refined_gas': 35
            }
            resource_value = sum(
                amount * resource_values.get(resource, 0)
                for resource, amount in fleet.resources.items()
                if resource != 'energy'
            )
            
            total += ship_value + drone_value + collector_value + resource_value
        
        self.total_assets = total
    
    def can_afford(self, costs: dict) -> bool:
        """Check if we can afford the specified costs"""
        if 'credits' in costs and costs['credits'] > self.credits:
            return False
        
        current_fleet = self.get_current_fleet()
        if not current_fleet:
            return False
        
        for resource, amount in costs.items():
            if resource != 'credits':
                if current_fleet.resources.get(resource, 0) < amount:
                    return False
        return True
    
    def deduct_resources(self, costs: dict) -> bool:
        """Deduct resources if we can afford them"""
        if not self.can_afford(costs):
            return False
        
        if 'credits' in costs:
            self.credits -= costs['credits']
        
        current_fleet = self.get_current_fleet()
        for resource, amount in costs.items():
            if resource != 'credits':
                current_fleet.remove_resource(resource, amount)
        
        return True
    
    @property
    def crew(self) -> int:
        """Get the current crew count"""
        current_fleet = self.get_current_fleet()
        if current_fleet:
            return current_fleet.mining_drones + current_fleet.gas_collectors
        return 0
        
    @property
    def power_usage(self) -> float:
        """Get the current power usage"""
        current_fleet = self.get_current_fleet()
        if current_fleet:
            return current_fleet.power_usage
        return 0
        
    def update_storage_capacity(self):
        """Update storage capacity based on storage facility level"""
        storage = self.buildings['storage_facility']
        for resource in ['metal', 'crystal']:
            self.storage[resource] = storage.calculate_capacity() 