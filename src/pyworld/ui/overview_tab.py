import tkinter as tk
from tkinter import ttk
from .mining_game import MiningGame
from .fleet_details import FleetDetailsDialog
from datetime import datetime

class OverviewTab(ttk.Frame):
    def __init__(self, parent, game_state):
        super().__init__(parent)
        self.game_state = game_state
        self.create_widgets()
        
        # Start update loop
        self.update_displays()
    
    def create_widgets(self):
        """Create widgets for the overview tab"""
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        
        # Left panel - Fleets
        self.fleet_frame = ttk.LabelFrame(self, text="Your Fleets", padding="10")
        self.fleet_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Fleet list
        self.fleet_tree = ttk.Treeview(
            self.fleet_frame,
            columns=('id', 'name', 'storage', 'location'),
            show='headings'
        )
        self.fleet_tree.heading('id', text='ID')
        self.fleet_tree.heading('name', text='Name')
        self.fleet_tree.heading('storage', text='Storage')
        self.fleet_tree.heading('location', text='Location')
        
        self.fleet_tree.column('id', width=0, stretch=False)  # Hide ID column
        self.fleet_tree.column('name', width=100)
        self.fleet_tree.column('storage', width=100)
        self.fleet_tree.column('location', width=150)
        
        # Bind select event
        self.fleet_tree.bind('<<TreeviewSelect>>', self.on_fleet_select)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.fleet_frame, orient="vertical", command=self.fleet_tree.yview)
        self.fleet_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid placement
        self.fleet_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Right panel - Fleet Details
        self.details_frame = ttk.LabelFrame(self, text="Fleet Details", padding="10")
        self.details_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        # Corporation info
        self.corp_frame = ttk.Frame(self.details_frame)
        self.corp_frame.pack(fill='x', pady=5)
        
        ttk.Label(self.corp_frame, text="Corporation:").pack(side='left')
        self.corp_name_label = ttk.Label(self.corp_frame, text=self.game_state.corporation_name)
        self.corp_name_label.pack(side='left', padx=5)
        
        ttk.Label(self.corp_frame, text="Total Assets:").pack(side='left', padx=(20, 0))
        self.total_assets_label = ttk.Label(self.corp_frame, text=f"{self.game_state.total_assets:,} Credits")
        self.total_assets_label.pack(side='left', padx=5)
        
        # Fleet info
        self.fleet_info_frame = ttk.Frame(self.details_frame)
        self.fleet_info_frame.pack(fill='both', expand=True, pady=10)
        
        # Fleet travel progress
        self.travel_frame = ttk.LabelFrame(self.fleet_info_frame, text="Travel Status", padding="10")
        self.travel_frame.pack(fill='x', pady=5)
        
        self.travel_status = ttk.Label(self.travel_frame, text="Not traveling")
        self.travel_status.pack(anchor='w')
        
        self.travel_progress = ttk.Progressbar(self.travel_frame, orient="horizontal", length=300, mode="determinate")
        self.travel_progress.pack(fill='x', pady=5)
        
        # Fleet probing progress
        self.probe_frame = ttk.LabelFrame(self.fleet_info_frame, text="Probing Status", padding="10")
        self.probe_frame.pack(fill='x', pady=5)
        
        self.probe_status = ttk.Label(self.probe_frame, text="Not probing")
        self.probe_status.pack(anchor='w')
        
        self.probe_progress = ttk.Progressbar(self.probe_frame, orient="horizontal", length=300, mode="determinate")
        self.probe_progress.pack(fill='x', pady=5)
        
        # Bottom panel
        self.action_frame = ttk.Frame(self)
        self.action_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
    
    def update_displays(self):
        """Update all displays in the overview tab"""
        # Store current selections
        avail_selected = self.fleet_tree.selection()
        
        # Remember the selected fleet id for restoring selection
        selected_fleet_id = None
        if avail_selected:
            item = self.fleet_tree.item(avail_selected[0])
            selected_fleet_id = item['values'][0]
        
        # Clear existing items
        for item in self.fleet_tree.get_children():
            self.fleet_tree.delete(item)
        
        # Update corporation info
        self.corp_name_label.config(text=self.game_state.corporation_name)
        self.total_assets_label.config(text=f"{self.game_state.total_assets:,} Credits")
        
        # Update fleet list
        for fleet in self.game_state.fleets:
            fleet_id = str(id(fleet))
            item_values = (
                fleet_id,
                f"Fleet {fleet.level}",
                f"{fleet.storage_used}/{fleet.storage_capacity}",
                fleet.current_location
            )
            
            # Check if item already exists
            exists = False
            for item in self.fleet_tree.get_children():
                if self.fleet_tree.item(item)['values'][0] == fleet_id:
                    self.fleet_tree.item(item, values=item_values)
                    exists = True
                    break
            
            if not exists:
                self.fleet_tree.insert('', 'end', values=item_values)
        
        # Restore selection if it was previously selected
        if selected_fleet_id:
            for item in self.fleet_tree.get_children():
                if self.fleet_tree.item(item)['values'][0] == selected_fleet_id:
                    self.fleet_tree.selection_set(item)
                    break
        
        # Update travel and probe info
        current_fleet = self.game_state.get_current_fleet()
        if current_fleet:
            if current_fleet.is_traveling:
                progress = current_fleet.get_travel_progress() * 100
                self.travel_progress['value'] = progress
                
                remaining = ""
                if current_fleet.travel_end:
                    time_left = (current_fleet.travel_end - datetime.now()).total_seconds()
                    if time_left > 0:
                        hours, remainder = divmod(time_left, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        remaining = f" - {int(hours)}h {int(minutes)}m {int(seconds)}s remaining"
                
                self.travel_status.config(
                    text=f"Traveling to {current_fleet.destination.name}{remaining}"
                )
            else:
                self.travel_progress['value'] = 0
                self.travel_status.config(text="Not traveling")
                
            if current_fleet.is_probing:
                progress = current_fleet.get_probe_progress() * 100
                self.probe_progress['value'] = progress
                
                remaining = ""
                if current_fleet.probe_end:
                    time_left = (current_fleet.probe_end - datetime.now()).total_seconds()
                    if time_left > 0:
                        hours, remainder = divmod(time_left, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        remaining = f" - {int(hours)}h {int(minutes)}m {int(seconds)}s remaining"
                
                self.probe_status.config(
                    text=f"Probing {current_fleet.probe_region.name}{remaining}"
                )
            else:
                self.probe_progress['value'] = 0
                self.probe_status.config(text="Not probing")
        else:
            self.travel_progress['value'] = 0
            self.travel_status.config(text="No fleet selected")
            self.probe_progress['value'] = 0
            self.probe_status.config(text="No fleet selected")
        
        # Schedule next update
        self.after(1000, self.update_displays)
    
    def on_fleet_select(self, event):
        """Handle fleet selection"""
        selection = self.fleet_tree.selection()
        if selection:
            # Get selected fleet and update buttons state
            pass
    
    def view_fleet_details(self):
        """Open the fleet details dialog"""
        selected = self.fleet_tree.selection()
        if not selected:
            return
            
        fleet_id = int(selected[0])
        fleet = next((f for f in self.game_state.fleets if f.id == fleet_id), None)
        if fleet:
            self.game_state.set_current_fleet(fleet_id)
            FleetDetailsDialog(self, fleet)
    
    def upgrade_ship(self):
        """Upgrade the selected ship"""
        selected = self.fleet_tree.selection()
        if not selected:
            return
            
        fleet_id = int(selected[0])
        fleet = next((f for f in self.game_state.fleets if f.id == fleet_id), None)
        if fleet:
            fleet.start_upgrade()
            self.update_displays()
    
    def buy_new_ship(self):
        """Buy a new ship"""
        # For now, just add a new freighter if we can afford it
        if self.game_state.credits >= 5000:
            self.game_state.credits -= 5000
            self.game_state.add_fleet(f"Fleet {len(self.game_state.fleets) + 1}")
            self.update_displays()
    
    def start_mining(self):
        """Start the mining mini-game"""
        selected = self.fleet_tree.selection()
        if not selected:
            return
            
        fleet_id = int(selected[0])
        fleet = next((f for f in self.game_state.fleets if f.id == fleet_id), None)
        
        if fleet and not fleet.is_traveling:
            # Launch mining game
            MiningGame(self, fleet, callback=self.update_displays) 