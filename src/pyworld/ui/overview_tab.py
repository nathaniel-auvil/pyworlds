import tkinter as tk
from tkinter import ttk

class OverviewTab(ttk.Frame):
    def __init__(self, parent, game_state):
        super().__init__(parent)
        self.game_state = game_state
        self.create_widgets()
        
        # Start update loop
        self.update_displays()
    
    def create_widgets(self):
        """Create the overview tab widgets"""
        # Corporation Info
        corp_frame = ttk.LabelFrame(self, text="Corporation Information", padding="5")
        corp_frame.pack(fill='x', padx=5, pady=5)
        
        # Corporation name and basic info
        ttk.Label(corp_frame, text="Corporation Name:", font=('TkDefaultFont', 10, 'bold')).pack(anchor='w')
        self.corp_name_label = ttk.Label(corp_frame, text=self.game_state.corporation_name)
        self.corp_name_label.pack(anchor='w', padx=5)
        
        ttk.Label(corp_frame, text="Total Assets:", font=('TkDefaultFont', 10, 'bold')).pack(anchor='w', pady=(10,0))
        self.total_assets_label = ttk.Label(corp_frame, text="0 Credits")
        self.total_assets_label.pack(anchor='w', padx=5)
        
        # Fleet Management
        fleet_frame = ttk.LabelFrame(self, text="Fleet Management", padding="5")
        fleet_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Fleet list
        self.create_fleet_list(fleet_frame)
        
        # Buttons for fleet management
        button_frame = ttk.Frame(fleet_frame)
        button_frame.pack(fill='x', pady=5)
        
        ttk.Button(button_frame, text="View Details", command=self.view_fleet_details).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Upgrade Ship", command=self.upgrade_ship).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Buy New Ship", command=self.buy_new_ship).pack(side='left', padx=5)
    
    def create_fleet_list(self, parent):
        """Create the fleet list table"""
        # Create treeview
        columns = ('name', 'ship_type', 'location', 'drones', 'collectors', 'storage')
        self.fleet_tree = ttk.Treeview(parent, columns=columns, show='headings')
        
        # Define column headings
        self.fleet_tree.heading('name', text='Fleet Name')
        self.fleet_tree.heading('ship_type', text='Ship Type')
        self.fleet_tree.heading('location', text='Current Location')
        self.fleet_tree.heading('drones', text='Mining Drones')
        self.fleet_tree.heading('collectors', text='Gas Collectors')
        self.fleet_tree.heading('storage', text='Storage')
        
        # Configure columns
        self.fleet_tree.column('name', width=150)
        self.fleet_tree.column('ship_type', width=100)
        self.fleet_tree.column('location', width=150)
        self.fleet_tree.column('drones', width=100)
        self.fleet_tree.column('collectors', width=100)
        self.fleet_tree.column('storage', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.fleet_tree.yview)
        self.fleet_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.fleet_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind selection event
        self.fleet_tree.bind('<<TreeviewSelect>>', self.on_fleet_select)
    
    def update_displays(self):
        """Update all displays in the overview tab"""
        # Update corporation info
        self.corp_name_label.config(text=self.game_state.corporation_name)
        self.total_assets_label.config(text=f"{self.game_state.total_assets:,} Credits")
        
        # Clear existing fleet list
        for item in self.fleet_tree.get_children():
            self.fleet_tree.delete(item)
        
        # Update fleet list
        for fleet in self.game_state.fleets:
            self.fleet_tree.insert('', 'end', values=(
                fleet.name,
                fleet.ship_type,
                fleet.current_location,
                fleet.mining_drones,
                fleet.gas_collectors,
                f"{fleet.storage_used}/{fleet.storage_capacity}"
            ))
        
        # Schedule next update
        self.after(1000, self.update_displays)
    
    def on_fleet_select(self, event):
        """Handle fleet selection"""
        selection = self.fleet_tree.selection()
        if selection:
            # Get selected fleet and update buttons state
            pass
    
    def view_fleet_details(self):
        """Show detailed information about the selected fleet"""
        selection = self.fleet_tree.selection()
        if not selection:
            return
        # Show fleet details dialog
    
    def upgrade_ship(self):
        """Open the ship upgrade interface"""
        selection = self.fleet_tree.selection()
        if not selection:
            return
        # Show ship upgrade dialog
    
    def buy_new_ship(self):
        """Open the interface to purchase a new ship"""
        # Show ship purchase dialog
        pass 