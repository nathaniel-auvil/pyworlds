from datetime import datetime, timedelta
from .ship import Mothership
from .station import SpaceStation
from .universe import Universe

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
        self.game_speed = 1.0
        self.mothership = Mothership()
        self.station = SpaceStation()
        self.universe = Universe()
        self.credits = 1000
        self.last_update = datetime.now().timestamp()
        
        # Travel state
        self.is_traveling = False
        self.travel_start = None
        self.travel_destination = None
        self.travel_duration = None
        self.current_region = next(iter(self.universe.regions.values()))  # Start in first region
        
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
    
    @property
    def crew(self) -> int:
        """Get the current crew count"""
        return self.mothership.current_crew
        
    @property
    def power_usage(self) -> float:
        """Get the current power usage"""
        return self.mothership.power_generation - self.mothership.available_power
        
    def update(self, current_time: float):
        """Update game state"""
        elapsed_time = current_time - self.last_update
        
        # Update mothership resources
        self.mothership.update_resources(elapsed_time, self.game_speed)
        
        # Update station
        self.station.update_trades()
        self.station.restock()
        
        # Update universe
        self.universe.update()
        
        # Update travel progress
        if self.is_traveling and self.travel_start:
            elapsed = datetime.now() - self.travel_start
            if elapsed >= self.travel_duration:
                self.complete_travel()
        
        self.last_update = current_time
    
    def start_travel(self, destination):
        """Start traveling to a new region"""
        if self.is_traveling:
            return False
            
        self.is_traveling = True
        self.travel_start = datetime.now()
        self.travel_destination = destination
        self.travel_duration = timedelta(hours=1)  # For now, all travel takes 1 hour
        
        # Deduct fuel cost
        fuel_cost = 10  # For now, fixed fuel cost
        self.mothership.resources['fuel'] = self.mothership.resources.get('fuel', 0) - fuel_cost
        
        return True
    
    def complete_travel(self):
        """Complete the current travel"""
        if not self.is_traveling:
            return
            
        self.current_region = self.travel_destination
        self.is_traveling = False
        self.travel_start = None
        self.travel_destination = None
        self.travel_duration = None
    
    @property
    def travel_progress(self) -> float:
        """Calculate travel progress as a value between 0 and 1"""
        if not self.is_traveling or not self.travel_start or not self.travel_duration:
            return 0.0
            
        elapsed = datetime.now() - self.travel_start
        return min(1.0, elapsed.total_seconds() / self.travel_duration.total_seconds())
    
    @property
    def travel_eta(self) -> datetime:
        """Calculate estimated time of arrival"""
        if not self.is_traveling or not self.travel_start or not self.travel_duration:
            return datetime.now()
            
        return self.travel_start + self.travel_duration
    
    def can_afford(self, costs: dict) -> bool:
        """Check if we can afford the given costs"""
        for resource, amount in costs.items():
            if resource == 'credits':
                if self.credits < amount:
                    return False
            elif self.mothership.resources.get(resource, 0) < amount:
                return False
        return True
    
    def deduct_resources(self, costs: dict):
        """Deduct resources based on costs"""
        for resource, amount in costs.items():
            if resource == 'credits':
                self.credits -= amount
            else:
                self.mothership.resources[resource] -= amount
    
    def update_storage_capacity(self):
        """Update storage capacity based on storage facility level"""
        storage = self.buildings['storage_facility']
        for resource in ['metal', 'crystal']:
            self.storage[resource] = storage.calculate_capacity() 