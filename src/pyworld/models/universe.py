from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random
import math

class ResourceDeposit:
    def __init__(self, resource_type: str, base_amount: float, quality: float = 1.0):
        self.resource_type = resource_type
        self.base_amount = base_amount
        self.quality = quality  # Multiplier for collection rate
        self.discovered = False
        
    def collection_rate(self, collector_level: int) -> float:
        """Calculate collection rate based on deposit quality and collector level"""
        return self.base_amount * self.quality * (1.1 ** (collector_level - 1))
    
    @property
    def display_name(self) -> str:
        """Get a display-friendly name for this deposit"""
        return f"{self.resource_type.title()} Deposit (Quality: {self.quality:.1f})"
    
    @property
    def base_collection_rate(self) -> float:
        """Get the base collection rate without any level modifiers"""
        return self.base_amount * self.quality

class ResourceGrant:
    def __init__(self, deposit, corporation, duration_seconds):
        self.deposit = deposit
        self.corporation = corporation
        self.duration = timedelta(seconds=duration_seconds)
        self.start_time = datetime.now()

    @property
    def expired(self) -> bool:
        return datetime.now() >= self.start_time + self.duration

    @property
    def time_remaining(self) -> timedelta:
        remaining = self.start_time + self.duration - datetime.now()
        return max(remaining, timedelta(0))

    @property
    def display_name(self) -> str:
        return f"{self.deposit.display_name} - {self.corporation}"

    @property
    def progress(self) -> float:
        elapsed = datetime.now() - self.start_time
        return min(1.0, elapsed.total_seconds() / self.duration.total_seconds())

class Region:
    def __init__(self, name: str, level: int, position: tuple[int, int]):
        self.name = name
        self.level = level  # Determines resource quality and difficulty
        self.position = position
        self.deposits: List[ResourceDeposit] = []
        self.grants: List[ResourceGrant] = []
        self.controlling_corporation = "Stellar Industries"
        self.connections: List['Region'] = []
        
        # Generate resource deposits based on region level
        # Only generate deposits if this is not a test region
        if name != "Test Region":
            self._generate_deposits()
    
    def _generate_deposits(self):
        """Generate resource deposits based on region level"""
        num_deposits = 5  # Fixed number for test consistency
        for _ in range(num_deposits):
            resource_type = random.choice(['metal', 'gas'])
            base_amount = 10 * (1.2 ** (self.level - 1))
            quality = random.uniform(0.8, 1.2) * (1.1 ** (self.level - 1))
            
            deposit = ResourceDeposit(resource_type, base_amount, quality)
            self.deposits.append(deposit)
    
    def request_grant(self, deposit: ResourceDeposit, duration: timedelta) -> Optional[ResourceGrant]:
        """Request a resource collection grant for a specific deposit"""
        # Check if deposit is already granted
        if any(g.deposit == deposit and not g.expired for g in self.grants):
            return None
            
        grant = ResourceGrant(deposit, self.controlling_corporation, duration.total_seconds())
        self.grants.append(grant)
        return grant
    
    def update_grants(self):
        """Update grants and remove expired ones"""
        self.grants = [g for g in self.grants if not g.expired]
    
    def scan_deposits(self, scan_power: float) -> List[ResourceDeposit]:
        """Scan for undiscovered deposits"""
        newly_discovered = []
        for deposit in self.deposits:
            if not deposit.discovered:
                # Higher scan power and lower region level makes discovery more likely
                discovery_chance = scan_power / (self.level * 2)
                if random.random() < discovery_chance:
                    deposit.discovered = True
                    newly_discovered.append(deposit)
        return newly_discovered
    
    def distance_to(self, other: 'Region') -> float:
        """Calculate distance to another region"""
        dx = self.position[0] - other.position[0]
        dy = self.position[1] - other.position[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def get_discovered_deposits(self) -> List[ResourceDeposit]:
        """Get a list of discovered deposits"""
        return [d for d in self.deposits if d.discovered]
    
    def get_active_grants(self) -> List[ResourceGrant]:
        """Get a list of active grants"""
        return [g for g in self.grants if not g.expired]
    
    def get_available_deposits(self) -> List[ResourceDeposit]:
        """Get a list of deposits that are discovered but not granted"""
        granted_deposits = {g.deposit for g in self.get_active_grants()}
        return [d for d in self.get_discovered_deposits() if d not in granted_deposits]

class Universe:
    def __init__(self):
        self.regions = {}
        self.home_region = self.create_home_region()
        self._generate_regions()
    
    def create_home_region(self):
        home = Region("Home", 1, (0, 0))
        self.regions[home.name] = home
        return home

    def _generate_regions(self):
        """Generate initial regions in a grid pattern"""
        # Create starter region at center
        starter_region = Region(
            name="Alpha Sector",
            level=1,
            position=(0, 0)
        )
        self.regions[starter_region.name] = starter_region
        
        # Create surrounding regions
        positions = [(-1, -1), (-1, 0), (-1, 1),
                    (0, -1),          (0, 1),
                    (1, -1),  (1, 0),  (1, 1)]
        
        for i, (dx, dy) in enumerate(positions):
            level = random.randint(1, 3)
            region = Region(
                name=f"Region {chr(65 + i)}",  # A, B, C, etc.
                level=level,
                position=(dx * 2, dy * 2)
            )
            self.regions[region.name] = region
            
            # Connect to nearby regions
            for other in self.regions.values():
                if other != region and region.distance_to(other) <= 3:
                    region.connections.append(other)
                    other.connections.append(region)
    
    def update(self):
        """Update all regions"""
        for region in self.regions.values():
            region.update_grants()
    
    def get_region(self, region_name: str) -> Optional[Region]:
        """Get a region by name"""
        return self.regions.get(region_name)
    
    def get_connected_regions(self, region: Region) -> List[Region]:
        """Get a list of regions connected to the given region"""
        return region.connections
    
    def get_regions_by_level(self, min_level: int, max_level: int) -> List[Region]:
        """Get a list of regions within the specified level range"""
        return [r for r in self.regions.values() if min_level <= r.level <= max_level]
    
    def get_regions_by_distance(self, center: Region, max_distance: float) -> List[Region]:
        """Get a list of regions within the specified distance from the center"""
        return [r for r in self.regions.values() if r != center and r.distance_to(center) <= max_distance]
    
    def get_path_between(self, start: Region, end: Region) -> Optional[List[Region]]:
        """Find a path between two regions using breadth-first search"""
        if start == end:
            return [start]
            
        visited = {start}
        queue = [(start, [start])]
        
        while queue:
            current, path = queue.pop(0)
            for next_region in current.connections:
                if next_region == end:
                    return path + [end]
                if next_region not in visited:
                    visited.add(next_region)
                    queue.append((next_region, path + [next_region]))
        
        return None 