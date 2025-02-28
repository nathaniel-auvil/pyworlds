from datetime import datetime
from .ship import Mothership
from .station import SpaceStation

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
        self.credits = 1000
        self.last_update = datetime.now().timestamp()
        
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
    
    def update(self, current_time: float):
        """Update game state"""
        elapsed_time = current_time - self.last_update
        
        # Update mothership resources
        self.mothership.update_resources(elapsed_time, self.game_speed)
        
        # Update station
        self.station.update_trades()
        self.station.restock()
        
        self.last_update = current_time
    
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