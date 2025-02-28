import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

class ResourceAmountDialog:
    def __init__(self, parent, title: str, max_amount: int):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.result = None
        self.max_amount = max_amount
        
        # Create and pack widgets
        ttk.Label(self.dialog, text="Amount:").pack(padx=5, pady=5)
        
        self.amount_var = tk.StringVar(value="0")
        self.amount_entry = ttk.Entry(self.dialog, textvariable=self.amount_var)
        self.amount_entry.pack(padx=5, pady=5)
        
        ttk.Label(self.dialog, text=f"Maximum: {max_amount}").pack(padx=5)
        
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="OK", command=self.ok).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side='left')
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self.dialog.wait_window()
    
    def ok(self):
        try:
            amount = int(self.amount_var.get())
            if amount < 0:
                messagebox.showerror("Invalid Input", "Amount cannot be negative")
                return
            if amount > self.max_amount:
                messagebox.showerror("Invalid Input", f"Amount cannot exceed {self.max_amount}")
                return
            self.result = amount
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number")
    
    def cancel(self):
        self.dialog.destroy()

class StationView(ttk.Frame):
    def __init__(self, parent, game_state):
        super().__init__(parent)
        self.game_state = game_state
        self.create_widgets()
        
        # Start update loop
        self.update_displays()
    
    def create_widgets(self):
        """Create the station view widgets"""
        # Trading section
        self.create_trading_interface()
        
        # Missions section
        self.create_missions_interface()
        
        # Blueprints section
        self.create_blueprints_interface()
    
    def create_trading_interface(self):
        """Create the trading interface"""
        trade_frame = ttk.LabelFrame(self, text="Trading", padding="5")
        trade_frame.pack(fill='x', padx=5, pady=5)
        
        # Headers
        headers = ["Resource", "Stock", "Buy Price", "Sell Price", "Actions"]
        for i, header in enumerate(headers):
            ttk.Label(trade_frame, text=header, font=('TkDefaultFont', 10, 'bold')).grid(
                row=0, column=i, padx=5, pady=5
            )
        
        # Trade rows
        self.trade_widgets = {}
        for i, (resource, trade) in enumerate(self.game_state.station.trades.items()):
            row = i + 1
            
            # Resource name
            ttk.Label(trade_frame, text=resource.title()).grid(
                row=row, column=0, padx=5, pady=2
            )
            
            # Stock
            stock_label = ttk.Label(trade_frame, text=str(trade.quantity))
            stock_label.grid(row=row, column=1, padx=5, pady=2)
            
            # Buy price
            buy_label = ttk.Label(trade_frame, text=f"{trade.buy_price:.1f}")
            buy_label.grid(row=row, column=2, padx=5, pady=2)
            
            # Sell price
            sell_label = ttk.Label(trade_frame, text=f"{trade.sell_price:.1f}")
            sell_label.grid(row=row, column=3, padx=5, pady=2)
            
            # Action buttons
            button_frame = ttk.Frame(trade_frame)
            button_frame.grid(row=row, column=4, padx=5, pady=2)
            
            buy_button = ttk.Button(
                button_frame, text="Buy",
                command=lambda r=resource: self.buy_resource(r)
            )
            buy_button.pack(side='left', padx=2)
            
            sell_button = ttk.Button(
                button_frame, text="Sell",
                command=lambda r=resource: self.sell_resource(r)
            )
            sell_button.pack(side='left', padx=2)
            
            # Store widget references
            self.trade_widgets[resource] = {
                'stock': stock_label,
                'buy_price': buy_label,
                'sell_price': sell_label,
                'buy_button': buy_button,
                'sell_button': sell_button
            }
    
    def create_missions_interface(self):
        """Create the missions interface"""
        missions_frame = ttk.LabelFrame(self, text="Available Missions", padding="5")
        missions_frame.pack(fill='x', padx=5, pady=5)
        
        self.mission_widgets = []
        for mission in self.game_state.station.available_missions:
            frame = ttk.Frame(missions_frame)
            frame.pack(fill='x', pady=2)
            
            # Mission info
            info_frame = ttk.Frame(frame)
            info_frame.pack(side='left', fill='x', expand=True)
            
            ttk.Label(info_frame, text=mission.name, font=('TkDefaultFont', 10, 'bold')).pack(anchor='w')
            ttk.Label(info_frame, text=mission.description).pack(anchor='w')
            
            # Requirements
            req_text = "Requirements: " + ", ".join(
                f"{amount} {res}" for res, amount in mission.requirements.items()
            )
            ttk.Label(info_frame, text=req_text).pack(anchor='w')
            
            # Rewards
            reward_text = "Rewards: " + ", ".join(
                f"{amount} {res}" for res, amount in mission.rewards.items()
            )
            ttk.Label(info_frame, text=reward_text).pack(anchor='w')
            
            # Time limit
            ttk.Label(info_frame, text=f"Time limit: {mission.time_limit} hours").pack(anchor='w')
            
            # Accept button
            ttk.Button(
                frame, text="Accept",
                command=lambda m=mission: self.accept_mission(m)
            ).pack(side='right', padx=5)
    
    def create_blueprints_interface(self):
        """Create the blueprints interface"""
        blueprints_frame = ttk.LabelFrame(self, text="Available Blueprints", padding="5")
        blueprints_frame.pack(fill='x', padx=5, pady=5)
        
        for blueprint in self.game_state.station.available_blueprints:
            frame = ttk.Frame(blueprints_frame)
            frame.pack(fill='x', pady=2)
            
            # Blueprint info
            info_frame = ttk.Frame(frame)
            info_frame.pack(side='left', fill='x', expand=True)
            
            ttk.Label(info_frame, text=blueprint.name, font=('TkDefaultFont', 10, 'bold')).pack(anchor='w')
            ttk.Label(info_frame, text=f"Type: {blueprint.module_type}").pack(anchor='w')
            
            # Requirements
            req_text = "Requirements: " + ", ".join(
                f"{module} level {level}" for module, level in blueprint.requirements.items()
            )
            ttk.Label(info_frame, text=req_text).pack(anchor='w')
            
            # Cost
            cost_text = "Cost: " + ", ".join(
                f"{amount} {res}" for res, amount in blueprint.cost.items()
            )
            ttk.Label(info_frame, text=cost_text).pack(anchor='w')
            
            # Purchase button
            ttk.Button(
                frame, text="Purchase",
                command=lambda b=blueprint: self.purchase_blueprint(b)
            ).pack(side='right', padx=5)
    
    def buy_resource(self, resource):
        """Buy resources from the station"""
        trade = self.game_state.station.trades[resource]
        
        # Ask for amount
        dialog = ResourceAmountDialog(self, f"Buy {resource.title()}", trade.quantity)
        if dialog.result is None:
            return
            
        amount = dialog.result
        total_cost = amount * trade.sell_price
        
        # Check if player can afford it
        if self.game_state.mothership.resources.get('credits', 0) < total_cost:
            messagebox.showerror(
                "Cannot Buy",
                "Insufficient credits!"
            )
            return
        
        # Try to buy
        if self.game_state.station.sell_to_ship(resource, amount, self.game_state.mothership):
            self.update_displays()
        else:
            messagebox.showerror(
                "Cannot Buy",
                "Transaction failed. Check station stock and ship capacity."
            )
    
    def sell_resource(self, resource):
        """Sell resources to the station"""
        trade = self.game_state.station.trades[resource]
        ship_amount = self.game_state.mothership.resources.get(resource, 0)
        
        # Ask for amount
        dialog = ResourceAmountDialog(self, f"Sell {resource.title()}", ship_amount)
        if dialog.result is None:
            return
            
        amount = dialog.result
        
        # Try to sell
        if self.game_state.station.buy_from_ship(resource, amount, self.game_state.mothership):
            self.update_displays()
        else:
            messagebox.showerror(
                "Cannot Sell",
                "Transaction failed. Check your resources and station capacity."
            )
    
    def accept_mission(self, mission):
        """Accept a mission"""
        if mission.start_time is not None:
            messagebox.showerror(
                "Cannot Accept",
                "Mission already in progress!"
            )
            return
        
        mission.start_time = datetime.now()
        messagebox.showinfo(
            "Mission Accepted",
            f"Mission '{mission.name}' accepted!\n"
            f"You have {mission.time_limit} hours to complete it."
        )
    
    def purchase_blueprint(self, blueprint):
        """Purchase a blueprint"""
        # Check requirements
        for module, required_level in blueprint.requirements.items():
            current_level = self.game_state.mothership.modules[module].level
            if current_level < required_level:
                messagebox.showerror(
                    "Cannot Purchase",
                    f"Requires {module} level {required_level}!"
                )
                return
        
        # Check if we can afford it
        if not self.game_state.can_afford(blueprint.cost):
            messagebox.showerror(
                "Cannot Purchase",
                "Insufficient resources!"
            )
            return
        
        # Purchase the blueprint
        self.game_state.deduct_resources(blueprint.cost)
        messagebox.showinfo(
            "Blueprint Purchased",
            f"Successfully purchased {blueprint.name} blueprint!"
        )
    
    def update_displays(self):
        """Update all displays"""
        # Update trade displays
        for resource, trade in self.game_state.station.trades.items():
            widgets = self.trade_widgets[resource]
            widgets['stock'].config(text=str(trade.quantity))
            widgets['buy_price'].config(text=f"{trade.buy_price:.1f}")
            widgets['sell_price'].config(text=f"{trade.sell_price:.1f}")
        
        # Schedule next update
        self.after(1000, self.update_displays) 