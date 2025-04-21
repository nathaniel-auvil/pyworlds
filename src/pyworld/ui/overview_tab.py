import tkinter as tk
from tkinter import ttk
from .mining_game import MiningGame
from .fleet_details import FleetDetailsDialog
from datetime import datetime
import tkinter.messagebox as messagebox
from ..models.universe import RegionVisibility

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
        
        # Container frame for height control
        self.container = ttk.Frame(self)
        self.container.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Fleet list frame
        self.fleet_frame = ttk.LabelFrame(self.container, text="Your Fleets", padding="10")
        self.fleet_frame.grid(row=0, column=0, sticky='nsew')
        self.fleet_frame.grid_rowconfigure(0, weight=1)
        self.fleet_frame.grid_columnconfigure(0, weight=1)
        
        # Fleet list
        self.fleet_tree = ttk.Treeview(
            self.fleet_frame,
            columns=('id', 'name', 'storage', 'location', 'progress'),
            show='headings',
            height=20  # Set number of visible rows
        )
        self.fleet_tree.heading('id', text='ID')
        self.fleet_tree.heading('name', text='Name')
        self.fleet_tree.heading('storage', text='Storage')
        self.fleet_tree.heading('location', text='Location')
        self.fleet_tree.heading('progress', text='Progress')
        
        self.fleet_tree.column('id', width=0, stretch=False)  # Hide ID column
        self.fleet_tree.column('name', width=150)
        self.fleet_tree.column('storage', width=150)
        self.fleet_tree.column('location', width=200)
        self.fleet_tree.column('progress', width=400)
        
        # Bind select event
        self.fleet_tree.bind('<<TreeviewSelect>>', self.on_fleet_select)
        self.fleet_tree.bind('<Button-3>', self.show_fleet_menu)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.fleet_frame, orient="vertical", command=self.fleet_tree.yview)
        self.fleet_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid placement
        self.fleet_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
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
            # Calculate progress and status
            progress = 0
            status = ""
            
            if fleet.is_traveling:
                progress = fleet.get_travel_progress() * 100
                if fleet.travel_end:
                    time_left = (fleet.travel_end - datetime.now()).total_seconds()
                    if time_left > 0:
                        hours, remainder = divmod(time_left, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        status = f"Traveling to {fleet.destination.name} - {int(hours)}h {int(minutes)}m {int(seconds)}s"
            elif fleet.is_probing:
                progress = fleet.get_probe_progress() * 100
                if fleet.probe_end:
                    time_left = (fleet.probe_end - datetime.now()).total_seconds()
                    if time_left > 0:
                        hours, remainder = divmod(time_left, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        status = f"Probing {fleet.probe_region.name} - {int(hours)}h {int(minutes)}m {int(seconds)}s"
            
            # Format progress display
            progress_text = f"{progress:.0f}%" if progress > 0 else ""
            
            # Insert fleet with progress
            item_id = self.fleet_tree.insert('', 'end', values=(
                fleet.id,
                fleet.name,
                f"{fleet.storage_used}/{fleet.storage_capacity:.0f}",
                fleet.current_location,
                f"{status} ({progress_text})" if status else ""
            ))
            
            # Restore selection if this was the previously selected fleet
            if selected_fleet_id == fleet.id:
                self.fleet_tree.selection_set(item_id)
                self.fleet_tree.focus(item_id)
        
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
            
        try:
            item = self.fleet_tree.item(selected[0])
            fleet_id = item['values'][0]  # First column contains the fleet ID
            fleet = next((f for f in self.game_state.fleets if f.id == fleet_id), None)
            
            if fleet:
                self.game_state.set_current_fleet(fleet_id)
                FleetDetailsDialog(self, fleet)
            else:
                messagebox.showerror("Error", "Selected fleet not found in game state.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view fleet details: {str(e)}")
    
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