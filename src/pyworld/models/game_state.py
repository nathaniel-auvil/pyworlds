from datetime import datetime
from .buildings import BuildingFactory

class GameState:
    def __init__(self):
        self.game_speed = 1.0
        
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
            'metal_mine': BuildingFactory.create_metal_mine(),
            'crystal_mine': BuildingFactory.create_crystal_mine(),
            'solar_plant': BuildingFactory.create_solar_plant(),
            'storage_facility': BuildingFactory.create_storage_facility(),
            'shipyard': BuildingFactory.create_shipyard(),
            'research_lab': BuildingFactory.create_research_lab()
        }
    
    def update_resources(self, elapsed_hours):
        """Update resources based on production rates and elapsed time"""
        for resource in ['metal', 'crystal']:
            mine = f"{resource}_mine"
            production = (
                self.buildings[mine].calculate_production() * 
                elapsed_hours * 
                self.game_speed
            )
            
            # Check storage capacity
            available_storage = self.storage[resource] - self.resources[resource]
            production = min(production, available_storage)
            
            self.resources[resource] += production
        
        # Update energy
        self.resources['energy'] = (
            self.buildings['solar_plant'].calculate_production() * 
            self.game_speed
        )
        
        self.resources['last_update'] = datetime.now().timestamp()
    
    def can_afford(self, costs):
        """Check if we can afford the given costs"""
        return all(
            self.resources[resource] >= amount 
            for resource, amount in costs.items()
        )
    
    def deduct_resources(self, costs):
        """Deduct resources based on costs"""
        for resource, amount in costs.items():
            self.resources[resource] -= amount
    
    def update_storage_capacity(self):
        """Update storage capacity based on storage facility level"""
        storage_building = self.buildings['storage_facility']
        capacity = storage_building.calculate_capacity()
        for resource in ['metal', 'crystal']:
            self.storage[resource] = capacity 