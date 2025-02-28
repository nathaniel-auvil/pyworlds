import tkinter as tk
from tkinter import ttk
from datetime import datetime

class StationView(ttk.Frame):
    def __init__(self, parent, game_state):
        super().__init__(parent, padding="5")
        self.game_state = game_state
        
        # Create notebook for different station services
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Trading interface
        self.trade_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.trade_frame, text="Trading")
        self.create_trade_interface()
        
        # Missions interface
        self.missions_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.missions_frame, text="Missions")
        self.create_missions_interface()
        
        # Blueprints interface
        self.blueprints_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.blueprints_frame, text="Blueprints")
        self.create_blueprints_interface()
    
    def create_trade_interface(self):
        # Create headers
        headers = ['Resource', 'Your Stock', 'Station Stock', 'Buy Price', 'Sell Price', 'Actions']
        for i, header in enumerate(headers):
            ttk.Label(self.trade_frame, text=header, font=('TkDefaultFont', 10, 'bold')).grid(
                row=0, column=i, padx=5, pady=5
            )
        
        # Create trade rows
        self.trade_widgets = {}
        for i, (resource, trade) in enumerate(self.game_state.station.trades.items()):
            row = i + 1
            
            # Resource name
            ttk.Label(self.trade_frame, text=resource.replace('_', ' ').title()).grid(
                row=row, column=0, padx=5, pady=2
            )
            
            # Your stock
            stock_label = ttk.Label(self.trade_frame, text="0")
            stock_label.grid(row=row, column=1, padx=5, pady=2)
            
            # Station stock
            station_stock_label = ttk.Label(self.trade_frame, text=str(trade.quantity))
            station_stock_label.grid(row=row, column=2, padx=5, pady=2)
            
            # Buy price
            buy_label = ttk.Label(self.trade_frame, text=str(trade.buy_price))
            buy_label.grid(row=row, column=3, padx=5, pady=2)
            
            # Sell price
            sell_label = ttk.Label(self.trade_frame, text=str(trade.sell_price))
            sell_label.grid(row=row, column=4, padx=5, pady=2)
            
            # Trade buttons frame
            trade_frame = ttk.Frame(self.trade_frame)
            trade_frame.grid(row=row, column=5, padx=5, pady=2)
            
            # Amount entry
            amount_var = tk.StringVar(value="100")
            amount_entry = ttk.Entry(trade_frame, textvariable=amount_var, width=8)
            amount_entry.pack(side=tk.LEFT, padx=2)
            
            # Buy button
            buy_btn = ttk.Button(
                trade_frame, text="Buy",
                command=lambda r=resource, a=amount_var: self.buy_resource(r, a)
            )
            buy_btn.pack(side=tk.LEFT, padx=2)
            
            # Sell button
            sell_btn = ttk.Button(
                trade_frame, text="Sell",
                command=lambda r=resource, a=amount_var: self.sell_resource(r, a)
            )
            sell_btn.pack(side=tk.LEFT, padx=2)
            
            self.trade_widgets[resource] = {
                'stock_label': stock_label,
                'station_stock_label': station_stock_label,
                'buy_label': buy_label,
                'sell_label': sell_label,
                'amount_entry': amount_entry,
                'buy_button': buy_btn,
                'sell_button': sell_btn
            }
    
    def create_missions_interface(self):
        # Mission list
        self.mission_list = ttk.Frame(self.missions_frame)
        self.mission_list.pack(fill=tk.BOTH, expand=True)
        
        self.mission_widgets = []
        for mission in self.game_state.station.available_missions:
            frame = ttk.LabelFrame(self.mission_list, text=mission.name, padding="5")
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Description
            ttk.Label(frame, text=mission.description, wraplength=400).pack(anchor=tk.W)
            
            # Requirements
            req_frame = ttk.Frame(frame)
            req_frame.pack(fill=tk.X, pady=5)
            ttk.Label(req_frame, text="Requirements:", font=('TkDefaultFont', 9, 'bold')).pack(side=tk.LEFT)
            for resource, amount in mission.requirements.items():
                ttk.Label(req_frame, text=f"{resource}: {amount}").pack(side=tk.LEFT, padx=5)
            
            # Rewards
            reward_frame = ttk.Frame(frame)
            reward_frame.pack(fill=tk.X, pady=5)
            ttk.Label(reward_frame, text="Rewards:", font=('TkDefaultFont', 9, 'bold')).pack(side=tk.LEFT)
            for resource, amount in mission.rewards.items():
                ttk.Label(reward_frame, text=f"{resource}: {amount}").pack(side=tk.LEFT, padx=5)
            
            # Time limit
            ttk.Label(frame, text=f"Time limit: {mission.time_limit} hours").pack(anchor=tk.W)
            
            # Accept button
            accept_btn = ttk.Button(
                frame, text="Accept Mission",
                command=lambda m=mission: self.accept_mission(m)
            )
            accept_btn.pack(pady=5)
            
            self.mission_widgets.append({
                'frame': frame,
                'accept_button': accept_btn
            })
    
    def create_blueprints_interface(self):
        # Blueprint list
        self.blueprint_list = ttk.Frame(self.blueprints_frame)
        self.blueprint_list.pack(fill=tk.BOTH, expand=True)
        
        self.blueprint_widgets = []
        for blueprint in self.game_state.station.available_blueprints:
            frame = ttk.LabelFrame(self.blueprint_list, text=blueprint.name, padding="5")
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Type
            ttk.Label(frame, text=f"Type: {blueprint.module_type}").pack(anchor=tk.W)
            
            # Requirements
            req_frame = ttk.Frame(frame)
            req_frame.pack(fill=tk.X, pady=5)
            ttk.Label(req_frame, text="Requirements:", font=('TkDefaultFont', 9, 'bold')).pack(side=tk.LEFT)
            for module, level in blueprint.requirements.items():
                ttk.Label(req_frame, text=f"{module} level {level}").pack(side=tk.LEFT, padx=5)
            
            # Cost
            cost_frame = ttk.Frame(frame)
            cost_frame.pack(fill=tk.X, pady=5)
            ttk.Label(cost_frame, text="Cost:", font=('TkDefaultFont', 9, 'bold')).pack(side=tk.LEFT)
            for resource, amount in blueprint.cost.items():
                ttk.Label(cost_frame, text=f"{resource}: {amount}").pack(side=tk.LEFT, padx=5)
            
            # Purchase button
            purchase_btn = ttk.Button(
                frame, text="Purchase Blueprint",
                command=lambda b=blueprint: self.purchase_blueprint(b)
            )
            purchase_btn.pack(pady=5)
            
            self.blueprint_widgets.append({
                'frame': frame,
                'purchase_button': purchase_btn
            })
    
    def update_displays(self):
        """Update all displays in the station view"""
        # Update trade displays
        for resource, widgets in self.trade_widgets.items():
            # Update your stock
            widgets['stock_label'].config(
                text=str(int(self.game_state.mothership.resources.get(resource, 0)))
            )
            
            # Update station stock and prices
            trade = self.game_state.station.trades[resource]
            widgets['station_stock_label'].config(text=str(trade.quantity))
            widgets['buy_label'].config(text=f"{trade.buy_price:.1f}")
            widgets['sell_label'].config(text=f"{trade.sell_price:.1f}")
    
    def buy_resource(self, resource, amount_var):
        """Buy resources from the station"""
        try:
            amount = int(amount_var.get())
            if amount <= 0:
                return
            
            result = self.game_state.station.sell_to_ship(resource, amount, self.game_state.mothership)
            if result is not None:
                self.update_displays()
            
        except ValueError:
            pass  # Invalid amount entered
    
    def sell_resource(self, resource, amount_var):
        """Sell resources to the station"""
        try:
            amount = int(amount_var.get())
            if amount <= 0:
                return
            
            result = self.game_state.station.buy_from_ship(resource, amount, self.game_state.mothership)
            if result is not None:
                self.update_displays()
            
        except ValueError:
            pass  # Invalid amount entered
    
    def accept_mission(self, mission):
        """Accept a mission"""
        if not mission.start_time:  # Mission not started yet
            mission.start_time = datetime.now()
    
    def purchase_blueprint(self, blueprint):
        """Purchase a blueprint"""
        # Check requirements
        for module, required_level in blueprint.requirements.items():
            if module not in self.game_state.mothership.modules:
                return
            if self.game_state.mothership.modules[module].level < required_level:
                return
        
        # Check if we can afford it
        if not self.game_state.can_afford(blueprint.cost):
            return
        
        # Purchase the blueprint
        self.game_state.deduct_resources(blueprint.cost)
        # TODO: Add blueprint to mothership's available modules 