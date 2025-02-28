from datetime import datetime
from typing import Dict, Optional, List

class Module:
    def __init__(self, name: str, level: int = 1, module_type: str = None):
        self.name = name
        self.level = level
        self.module_type = module_type
        self.base_power_usage = 10
        self.base_crew_required = 2
        self.is_active = True
        self.current_upgrade = None
        
    def power_usage(self) -> float:
        """Calculate power usage at current level"""
        return self.base_power_usage * (1.1 ** (self.level - 1))
        
    def crew_required(self) -> int:
        """Calculate crew requirement at current level"""
        return self.base_crew_required * self.level
        
    def can_activate(self, ship) -> bool:
        """Check if module can be activated based on power and crew"""
        return (ship.available_power >= self.power_usage() and 
                ship.available_crew >= self.crew_required())

class ResourceCollector(Module):
    def __init__(self, name: str, resource_type: str, base_collection_rate: float):
        super().__init__(name, module_type="collector")
        self.resource_type = resource_type
        self.base_collection_rate = base_collection_rate
        
    def collection_rate(self) -> float:
        """Calculate collection rate at current level"""
        return self.base_collection_rate * (1.25 ** (self.level - 1))

class StorageModule(Module):
    def __init__(self, name: str, resource_type: str, base_capacity: int):
        super().__init__(name, module_type="storage")
        self.resource_type = resource_type
        self.base_capacity = base_capacity
        
    def capacity(self) -> int:
        """Calculate storage capacity at current level"""
        return self.base_capacity * self.level

class ProductionModule(Module):
    def __init__(self, name: str, production_type: str, base_production_rate: float):
        super().__init__(name, module_type="production")
        self.production_type = production_type
        self.base_production_rate = base_production_rate
        
    def production_rate(self) -> float:
        """Calculate production rate at current level"""
        return self.base_production_rate * (1.2 ** (self.level - 1))

class Ship:
    def __init__(self, name: str):
        self.name = name
        self.modules: Dict[str, Module] = {}
        self.resources: Dict[str, float] = {
            'metal': 0,
            'gas': 0,
            'energy': 0,
            'refined_metal': 0,
            'refined_gas': 0
        }
        self.max_crew = 0
        self.current_crew = 0
        self.max_power = 0
        self.power_generation = 0
        
    @property
    def available_power(self) -> float:
        """Calculate available power"""
        used_power = sum(module.power_usage() for module in self.modules.values() 
                        if module.is_active)
        return self.power_generation - used_power
        
    @property
    def available_crew(self) -> int:
        """Calculate available crew"""
        assigned_crew = sum(module.crew_required() for module in self.modules.values() 
                          if module.is_active)
        return self.current_crew - assigned_crew

class Mothership(Ship):
    def __init__(self, name: str = "Mothership Alpha"):
        super().__init__(name)
        # Initialize with basic modules
        self.modules = {
            'mining_drones': ResourceCollector(
                name="Mining Drones",
                resource_type="metal",
                base_collection_rate=10
            ),
            'gas_collector': ResourceCollector(
                name="Gas Collector",
                resource_type="gas",
                base_collection_rate=8
            ),
            'power_core': Module(
                name="Power Core",
                module_type="power"
            ),
            'cargo_hold': StorageModule(
                name="Cargo Hold",
                resource_type="general",
                base_capacity=1000
            ),
            'crew_quarters': Module(
                name="Crew Quarters",
                module_type="life_support"
            ),
            'drone_factory': ProductionModule(
                name="Drone Factory",
                production_type="drones",
                base_production_rate=1
            )
        }
        
        # Initialize starting resources
        self.resources = {
            'metal': 500,
            'gas': 300,
            'energy': 1000,
            'refined_metal': 0,
            'refined_gas': 0,
            'last_update': datetime.now().timestamp()
        }
        
        # Initialize crew and power
        self.max_crew = 50
        self.current_crew = 20
        self.max_power = 1000
        self.power_generation = 500
        
    def update_resources(self, elapsed_time: float, game_speed: float = 1.0):
        """Update resources based on active modules and elapsed time"""
        elapsed_hours = (elapsed_time * game_speed) / 3600  # Convert to hours
        
        # Update resource collection
        for module in self.modules.values():
            if not module.is_active:
                continue
                
            if isinstance(module, ResourceCollector):
                resource = module.resource_type
                collected = module.collection_rate() * elapsed_hours
                
                # Check storage capacity
                storage_module = next(
                    (m for m in self.modules.values() 
                     if isinstance(m, StorageModule) and 
                     (m.resource_type == resource or m.resource_type == "general")),
                    None
                )
                
                if storage_module:
                    available_storage = storage_module.capacity() - self.resources[resource]
                    collected = min(collected, available_storage)
                    
                self.resources[resource] += collected
            
            elif isinstance(module, ProductionModule):
                # Handle production modules (to be implemented)
                pass
        
        # Update timestamp
        self.resources['last_update'] = datetime.now().timestamp() 