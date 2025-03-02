import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

from .station_view import StationView
from .universe_view import UniverseView
from .overview_tab import OverviewTab

class MainWindow(tk.Tk):
    def __init__(self, game_state):
        super().__init__()
        
        self.game_state = game_state
        self.title("PyWorlds")
        self.geometry("1024x768")
        
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.create_gui()
        
        # Initialize update loop
        self.last_update = datetime.now()
        self.update_displays()
    
    def create_gui(self):
        """Create the main GUI elements"""
        # Create top bar with resources
        self.create_resource_display()
        
        # Create main notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        
        # Create overview tab (default)
        self.overview_tab = OverviewTab(self.notebook, self.game_state)
        self.notebook.add(self.overview_tab, text="Overview")
        
        # Create universe view
        self.universe_view = UniverseView(self.notebook, self.game_state)
        self.notebook.add(self.universe_view, text="Universe Map")
        
        # Create station view
        self.station_view = StationView(self.notebook, self.game_state)
        self.notebook.add(self.station_view, text="Space Station")
        
        # Create status bar
        self.status_bar = ttk.Label(self, text="", relief='sunken')
        self.status_bar.grid(row=2, column=0, sticky='ew')
    
    def create_resource_display(self):
        """Create the resource display bar"""
        resource_frame = ttk.Frame(self)
        resource_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        # Credits
        ttk.Label(resource_frame, text="Credits:").pack(side='left', padx=5)
        self.credits_label = ttk.Label(resource_frame, text="0")
        self.credits_label.pack(side='left', padx=5)
        
        # Separator
        ttk.Separator(resource_frame, orient='vertical').pack(side='left', padx=10, fill='y')
        
        # Resources
        self.resource_labels = {}
        for resource in ['metal', 'gas', 'energy', 'refined_metal', 'refined_gas']:
            ttk.Label(
                resource_frame,
                text=f"{resource.replace('_', ' ').title()}:"
            ).pack(side='left', padx=5)
            
            label = ttk.Label(resource_frame, text="0/0")
            label.pack(side='left', padx=5)
            self.resource_labels[resource] = label
            
            if resource != 'refined_gas':  # Don't add separator after last resource
                ttk.Separator(resource_frame, orient='vertical').pack(
                    side='left', padx=10, fill='y'
                )
    
    def update_displays(self):
        """Update all displays"""
        now = datetime.now()
        dt = (now - self.last_update).total_seconds()
        self.last_update = now
        
        # Update game state
        self.game_state.update(dt)
        
        # Update resource displays
        self.credits_label.config(text=f"{self.game_state.credits:,.0f}")
        
        current_fleet = self.game_state.get_current_fleet()
        if current_fleet:
            for resource, label in self.resource_labels.items():
                amount = current_fleet.resources.get(resource, 0)
                capacity = current_fleet.get_resource_capacity(resource)
                label.config(text=f"{amount:,.0f}/{capacity:,.0f}")
        else:
            for label in self.resource_labels.values():
                label.config(text="0/0")
        
        # Update status bar
        if current_fleet and current_fleet.is_traveling:
            remaining = current_fleet.travel_end - now
            if remaining.total_seconds() > 0:
                self.status_bar.config(
                    text=f"Traveling to {current_fleet.destination} - "
                    f"ETA: {str(remaining).split('.')[0]}"
                )
            else:
                current_fleet.complete_travel()
                self.status_bar.config(text=f"Arrived at {current_fleet.current_location}")
        elif current_fleet:
            self.status_bar.config(
                text=f"Current location: {current_fleet.current_location}"
            )
        else:
            self.status_bar.config(text="No fleet selected")
        
        # Schedule next update
        self.after(100, self.update_displays)
    
    def run(self):
        """Run the main window"""
        self.mainloop() 