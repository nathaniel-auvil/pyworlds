import tkinter as tk
from tkinter import ttk
from .mining_game import MiningGame
from .fleet_details import FleetDetailsDialog
from datetime import datetime
import tkinter.messagebox as messagebox

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
        self.fleet_tree.bind('<Button-3>', self.show_fleet_menu)
        
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
        
        # Create fleet action menu
        self.fleet_menu = tk.Menu(self, tearoff=0)
        self.fleet_menu.add_command(label="View Details", command=self.view_fleet_details)
        self.fleet_menu.add_command(label="Probe System", command=self.probe_system)
        self.fleet_menu.add_command(label="Start Mining", command=self.start_mining)
        self.fleet_menu.add_command(label="Upgrade Fleet", command=self.upgrade_ship)
        self.fleet_menu.add_separator()
        self.fleet_menu.add_command(label="Buy New Fleet", command=self.buy_new_ship)
    
    def update_displays(self):
        """Update the displays with current information"""
        # Store current selection
        selection = self.fleet_tree.selection()
        selected_fleet_id = None
        if selection:
            item = self.fleet_tree.item(selection[0])
            selected_fleet_id = item['values'][0]
        
        # Clear existing items
        for item in self.fleet_tree.get_children():
            self.fleet_tree.delete(item)
        
        # Add fleets
        for fleet in self.game_state.fleets:
            item_id = self.fleet_tree.insert('', 'end', values=(
                fleet.id,  # First column is the fleet ID
                fleet.name,
                f"{fleet.storage_used}/{fleet.storage_capacity:.0f}",
                fleet.current_location
            ))
            
            # Restore selection if this was the previously selected fleet
            if selected_fleet_id == fleet.id:
                self.fleet_tree.selection_set(item_id)
                self.fleet_tree.focus(item_id)
        
        # Update corporation info
        self.corp_name_label.config(text=self.game_state.corporation_name)
        self.total_assets_label.config(text=f"{self.game_state.total_assets:,} Credits")
        
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
            # Get selected fleet
            item = self.fleet_tree.item(selection[0])
            fleet_id = item['values'][0]  # First column contains the fleet ID
            fleet = next((f for f in self.game_state.fleets if f.id == fleet_id), None)
            
            if fleet:
                # Set as current fleet
                self.game_state.set_current_fleet(fleet_id)
                
                # Update menu items based on fleet state
                self.fleet_menu.entryconfig("Probe System", state='normal')
                if not fleet.current_region or fleet.current_region.visibility == RegionVisibility.EXPLORED:
                    self.fleet_menu.entryconfig("Probe System", state='disabled')
                
                self.fleet_menu.entryconfig("Start Mining", state='normal')
                if not fleet.current_region or fleet.current_region.visibility != RegionVisibility.EXPLORED:
                    self.fleet_menu.entryconfig("Start Mining", state='disabled')
                
                self.fleet_menu.entryconfig("Upgrade Fleet", state='normal')
                if fleet.is_traveling or fleet.is_probing:
                    self.fleet_menu.entryconfig("Upgrade Fleet", state='disabled')
    
    def view_fleet_details(self):
        """Open the fleet details dialog"""
        selected = self.fleet_tree.selection()
        if not selected:
            return
            
        item = self.fleet_tree.item(selected[0])
        fleet_id = item['values'][0]  # First column contains the fleet ID
        fleet = next((f for f in self.game_state.fleets if f.id == fleet_id), None)
        if fleet:
            self.game_state.set_current_fleet(fleet_id)
            FleetDetailsDialog(self, fleet)
    
    def upgrade_ship(self):
        """Upgrade the selected ship"""
        selected = self.fleet_tree.selection()
        if not selected:
            return
            
        item = self.fleet_tree.item(selected[0])
        fleet_id = item['values'][0]  # First column contains the fleet ID
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
            
        item = self.fleet_tree.item(selected[0])
        fleet_id = item['values'][0]  # First column contains the fleet ID
        fleet = next((f for f in self.game_state.fleets if f.id == fleet_id), None)
        
        if fleet and not fleet.is_traveling:
            # Launch mining game
            MiningGame(self, fleet, callback=self.update_displays)
    
    def show_fleet_menu(self, event):
        """Show the fleet action menu"""
        # Select the item under cursor
        item = self.fleet_tree.identify_row(event.y)
        if item:
            self.fleet_tree.selection_set(item)
            self.fleet_tree.focus(item)
            self.on_fleet_select(None)  # Update selection
            
            # Get the fleet
            item_data = self.fleet_tree.item(item)
            fleet_id = item_data['values'][0]  # First column contains the fleet ID
            fleet = next((f for f in self.game_state.fleets if f.id == fleet_id), None)
            
            if fleet:
                # Update menu items based on fleet state
                self.fleet_menu.entryconfig("Probe System", state='normal')
                if not fleet.current_region or fleet.current_region.visibility == RegionVisibility.EXPLORED:
                    self.fleet_menu.entryconfig("Probe System", state='disabled')
                
                self.fleet_menu.entryconfig("Start Mining", state='normal')
                if not fleet.current_region or fleet.current_region.visibility != RegionVisibility.EXPLORED:
                    self.fleet_menu.entryconfig("Start Mining", state='disabled')
                
                self.fleet_menu.entryconfig("Upgrade Fleet", state='normal')
                if fleet.is_traveling or fleet.is_probing:
                    self.fleet_menu.entryconfig("Upgrade Fleet", state='disabled')
                
                # Show menu
                self.fleet_menu.post(event.x_root, event.y_root)
    
    def probe_system(self):
        """Initiate probing of the current system"""
        selection = self.fleet_tree.selection()
        if not selection:
            return
            
        fleet_id = int(selection[0])
        fleet = next((f for f in self.game_state.fleets if f.id == fleet_id), None)
        
        if not fleet or not fleet.current_region:
            return
            
        # Check if system is already probed
        if fleet.current_region.visibility == RegionVisibility.EXPLORED:
            messagebox.showwarning("Already Probed", "This system has already been probed.")
            return
            
        # Start probing
        try:
            fleet.start_probing(fleet.current_region)
            probe_seconds = 10 * fleet.current_region.level
            messagebox.showinfo(
                "Probing Started",
                f"Your fleet has started probing {fleet.current_region.name}. " +
                f"Estimated completion in {probe_seconds} seconds."
            )
        except Exception as e:
            messagebox.showerror("Probing Failed", str(e)) 