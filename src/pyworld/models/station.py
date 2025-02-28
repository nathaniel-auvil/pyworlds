from typing import Dict, List, Optional
from datetime import datetime, timedelta

class Trade:
    def __init__(self, resource: str, buy_price: float, sell_price: float, quantity: int):
        self.resource = resource
        self.buy_price = buy_price  # Station buys at this price
        self.sell_price = sell_price  # Station sells at this price
        self.quantity = quantity  # Available quantity
        self.last_update = datetime.now()

class Mission:
    def __init__(self, name: str, description: str, requirements: Dict[str, int], 
                 rewards: Dict[str, int], time_limit: int):
        self.name = name
        self.description = description
        self.requirements = requirements  # Dict of resource: amount
        self.rewards = rewards  # Dict of resource: amount
        self.time_limit = time_limit  # Time limit in hours
        self.start_time = None
        self.completed = False

class Blueprint:
    def __init__(self, name: str, module_type: str, cost: Dict[str, int], 
                 requirements: Dict[str, int]):
        self.name = name
        self.module_type = module_type
        self.cost = cost  # Cost in resources
        self.requirements = requirements  # Required module levels

class SpaceStation:
    def __init__(self, name: str = "Alpha Station"):
        self.name = name
        self.trades: Dict[str, Trade] = {
            'metal': Trade('metal', 8, 10, 1000),
            'gas': Trade('gas', 12, 15, 1000),
            'refined_metal': Trade('refined_metal', 15, 20, 500),
            'refined_gas': Trade('refined_gas', 20, 25, 500)
        }
        
        self.available_missions: List[Mission] = [
            Mission(
                "Resource Gathering",
                "Collect resources for the station's needs",
                {'metal': 100, 'gas': 50},
                {'credits': 1000, 'refined_metal': 20},
                24  # 24 hours time limit
            )
        ]
        
        self.available_blueprints: List[Blueprint] = [
            Blueprint(
                "Advanced Mining Drones",
                "collector",
                {'credits': 5000, 'refined_metal': 100},
                {'mining_drones': 5}  # Requires level 5 mining drones
            )
        ]
        
        self.last_restock = datetime.now()
        self.restock_interval = timedelta(hours=1)
    
    def update_trades(self):
        """Update trade prices and quantities"""
        current_time = datetime.now()
        
        for trade in self.trades.values():
            time_diff = (current_time - trade.last_update).total_seconds() / 3600
            
            # Update prices based on quantity and time
            if trade.quantity < 200:  # Low stock
                trade.buy_price *= 0.95  # Lower buying price
                trade.sell_price *= 1.05  # Increase selling price
            elif trade.quantity > 800:  # High stock
                trade.buy_price *= 1.05  # Increase buying price
                trade.sell_price *= 0.95  # Lower selling price
            
            trade.last_update = current_time
    
    def restock(self):
        """Restock resources if enough time has passed"""
        current_time = datetime.now()
        
        if current_time - self.last_restock >= self.restock_interval:
            for trade in self.trades.values():
                # Gradually restore quantity to 1000
                if trade.quantity < 1000:
                    trade.quantity = min(1000, trade.quantity + 100)
            
            self.last_restock = current_time
    
    def buy_from_ship(self, resource: str, amount: int, ship) -> Optional[float]:
        """Buy resources from a ship"""
        if resource not in self.trades:
            return None
            
        trade = self.trades[resource]
        if trade.quantity + amount > 1000:  # Station capacity
            return None
            
        if ship.resources[resource] < amount:
            return None
            
        total_price = amount * trade.buy_price
        trade.quantity += amount
        ship.resources[resource] -= amount
        ship.resources['credits'] = ship.resources.get('credits', 0) + total_price
        
        return total_price
    
    def sell_to_ship(self, resource: str, amount: int, ship) -> Optional[float]:
        """Sell resources to a ship"""
        if resource not in self.trades:
            return None
            
        trade = self.trades[resource]
        if trade.quantity < amount:
            return None
            
        total_price = amount * trade.sell_price
        if ship.resources.get('credits', 0) < total_price:
            return None
            
        trade.quantity -= amount
        ship.resources[resource] = ship.resources.get(resource, 0) + amount
        ship.resources['credits'] -= total_price
        
        return total_price
    
    def check_mission_completion(self, mission: Mission, ship) -> bool:
        """Check if a ship has completed a mission's requirements"""
        if not mission.start_time:
            return False
            
        # Check if mission has expired
        time_elapsed = (datetime.now() - mission.start_time).total_seconds() / 3600
        if time_elapsed > mission.time_limit:
            return False
            
        # Check if ship has required resources
        for resource, amount in mission.requirements.items():
            if ship.resources.get(resource, 0) < amount:
                return False
        
        # Mission completed, give rewards
        for resource, amount in mission.requirements.items():
            ship.resources[resource] -= amount
            
        for resource, amount in mission.rewards.items():
            ship.resources[resource] = ship.resources.get(resource, 0) + amount
            
        mission.completed = True
        return True 