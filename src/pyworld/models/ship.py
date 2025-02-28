from typing import Dict, List, Optional
from datetime import datetime, timedelta

class Module:
    def __init__(self, name: str, module_type: str):
        self.name = name
        self.module_type = module_type
        self.level = 1
        self.is_active = True
        self.upgrade_start = None
        self.upgrade_end = None
        
    @property
    def id(self) -> str:
        """Get the unique identifier for this module"""
        return self.name.lower().replace(' ', '_')
        
    def power_usage(self) -> float:
        """Calculate power usage at current level"""
        base_power = 10  # Base power usage
        return base_power * (1.1 ** (self.level - 1))
        
    def crew_required(self) -> int:
        """Calculate crew required at current level"""
        base_crew = 2  # Base crew requirement
        return max(1, int(base_crew * (1.1 ** (self.level - 1))))
        
    def start_upgrade(self):
        """Start upgrading this module"""
        if self.upgrade_start is not None:
            return False
        
        self.upgrade_start = datetime.now()
        self.upgrade_end = self.upgrade_start + timedelta(minutes=5)
        return True
        
    def complete_upgrade(self) -> bool:
        """Check if upgrade is complete and apply it"""
        if not self.upgrade_start or not self.upgrade_end:
            return False
            
        if datetime.now() >= self.upgrade_end:
            self.level += 1
            self.upgrade_start = None
            self.upgrade_end = None
            return True
            
        return False

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
            'refined_gas': 0,
            'fuel': 1000  # Starting fuel
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
        
    def get_resource_capacity(self, resource: str) -> float:
        """Get the storage capacity for a specific resource"""
        # Find storage modules that can store this resource
        storage_modules = [
            m for m in self.modules.values()
            if isinstance(m, StorageModule) and 
            (m.resource_type == resource or m.resource_type == "general")
        ]
        
        # Sum up their capacities
        return sum(m.capacity() for m in storage_modules) if storage_modules else 0

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
            'fuel': 1000,  # Starting fuel
            'last_update': datetime.now().timestamp()
        }
        
        # Initialize crew and power
        self.max_crew = 50
        self.current_crew = 20
        self.max_power = 1000
        self.power_generation = 500
        
        # Resource prices in credits
        self.resource_prices = {
            'metal': 1,
            'gas': 2,
            'refined_metal': 5,
            'refined_gas': 10,
            'fuel': 3
        }
    
    @property
    def crew(self) -> int:
        """Get the current crew count"""
        return self.current_crew
        
    @property
    def power_usage(self) -> float:
        """Calculate total power usage from all active modules"""
        return sum(
            module.power_usage() for module in self.modules.values()
            if module.is_active
        )
        
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
    
    def total_resource_value(self) -> float:
        """Calculate the total value of all resources in credits"""
        return sum(
            amount * self.resource_prices.get(resource, 0)
            for resource, amount in self.resources.items()
            if resource != 'last_update'  # Skip the timestamp
        ) 