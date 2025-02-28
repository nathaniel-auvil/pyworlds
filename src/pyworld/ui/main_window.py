import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

from .station_view import StationView
from .universe_view import UniverseView

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
        
        # Create mothership view
        self.mothership_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.mothership_frame, text="Mothership")
        self.create_mothership_view()
        
        # Create station view
        self.station_view = StationView(self.notebook, self.game_state)
        self.notebook.add(self.station_view, text="Space Station")
        
        # Create universe view
        self.universe_view = UniverseView(self.notebook, self.game_state)
        self.notebook.add(self.universe_view, text="Universe Map")
        
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
    
    def create_mothership_view(self):
        """Create the mothership view tab"""
        # Create frames
        self.mothership_frame.grid_rowconfigure(0, weight=1)
        self.mothership_frame.grid_columnconfigure(1, weight=1)
        
        # Left panel with ship status
        status_frame = ttk.Frame(self.mothership_frame, padding="5")
        status_frame.grid(row=0, column=0, sticky='nsew')
        
        # Ship status
        ship_status = ttk.LabelFrame(status_frame, text="Ship Status", padding="5")
        ship_status.pack(fill='x', pady=5)
        
        # Crew info
        self.crew_label = ttk.Label(ship_status, text="Crew: 0/0")
        self.crew_label.pack(anchor='w')
        
        # Power info
        self.power_label = ttk.Label(ship_status, text="Power: 0/0")
        self.power_label.pack(anchor='w')
        
        # Right panel with modules
        module_frame = ttk.Frame(self.mothership_frame, padding="5")
        module_frame.grid(row=0, column=1, sticky='nsew')
        
        # Create module displays
        self.create_modules_display(module_frame)
    
    def create_modules_display(self, module_frame):
        """Create the module display area"""
        # Module grid
        self.module_widgets = {}
        
        for i, (module_id, module) in enumerate(self.game_state.mothership.modules.items()):
            # Create module frame
            frame = ttk.LabelFrame(
                module_frame,
                text=module.name.replace('_', ' ').title(),
                padding="5"
            )
            frame.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='nsew')
            
            # Module level
            level_frame = ttk.Frame(frame)
            level_frame.pack(fill='x')
            
            ttk.Label(level_frame, text="Level:").pack(side='left')
            level_label = ttk.Label(level_frame, text=str(module.level))
            level_label.pack(side='left', padx=5)
            
            # Info button
            ttk.Button(
                level_frame, text="Info",
                command=lambda m=module: self.show_module_info(m)
            ).pack(side='right')
            
            # Upgrade progress
            progress_var = tk.DoubleVar(value=0)
            progress_bar = ttk.Progressbar(
                frame, mode='determinate',
                variable=progress_var
            )
            progress_bar.pack(fill='x', pady=5)
            
            # Time remaining
            time_label = ttk.Label(frame, text="")
            time_label.pack()
            
            # Upgrade button
            upgrade_btn = ttk.Button(
                frame, text="Upgrade",
                command=lambda m=module: self.upgrade_module(m)
            )
            upgrade_btn.pack(pady=5)
            
            # Store widgets
            self.module_widgets[module_id] = {
                'level': level_label,
                'progress': progress_var,
                'time': time_label,
                'upgrade_button': upgrade_btn
            }
    
    def show_module_info(self, module):
        """Show detailed information about a module"""
        from .module_info_popup import ModuleInfoPopup  # Import here to avoid circular dependency
        ModuleInfoPopup(self, module)
    
    def upgrade_module(self, module):
        """Start upgrading a module"""
        # Calculate costs
        costs = self.calculate_upgrade_costs(module)
        
        # Check if we can afford it
        if not self.game_state.can_afford(costs):
            messagebox.showerror(
                "Cannot Upgrade",
                "Insufficient resources for upgrade!"
            )
            return
        
        # Start upgrade
        self.game_state.deduct_resources(costs)
        module.start_upgrade()
        
        # Update UI
        widgets = self.module_widgets[module.id]
        widgets['upgrade_button']['state'] = 'disabled'
    
    def calculate_upgrade_costs(self, module):
        """Calculate the costs to upgrade a module"""
        base_cost = 100 * (module.level + 1)
        return {
            'metal': base_cost,
            'refined_metal': base_cost // 2,
            'energy': base_cost * 2
        }
    
    def calculate_upgrade_progress(self, module):
        """Calculate the current upgrade progress"""
        if not module.upgrade_start:
            return 0.0
        
        elapsed = datetime.now() - module.upgrade_start
        total_time = module.upgrade_end - module.upgrade_start
        return min(1.0, elapsed.total_seconds() / total_time.total_seconds())
    
    def calculate_remaining_time(self, module):
        """Calculate the remaining upgrade time"""
        if not module.upgrade_start:
            return None
        
        remaining = module.upgrade_end - datetime.now()
        if remaining.total_seconds() <= 0:
            return None
        
        return remaining
    
    def complete_module_upgrade(self, module):
        """Complete a module upgrade"""
        module.complete_upgrade()
        
        # Update UI
        widgets = self.module_widgets[module.id]
        widgets['level'].config(text=str(module.level))
        widgets['progress'].set(0)
        widgets['time'].config(text="")
        widgets['upgrade_button']['state'] = 'normal'
        
        messagebox.showinfo(
            "Upgrade Complete",
            f"{module.name.replace('_', ' ').title()} upgraded to level {module.level}!"
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
        
        for resource, label in self.resource_labels.items():
            amount = self.game_state.mothership.resources.get(resource, 0)
            capacity = self.game_state.mothership.get_resource_capacity(resource)
            label.config(text=f"{amount:,.0f}/{capacity:,.0f}")
        
        # Update ship status
        crew = self.game_state.mothership.crew
        max_crew = self.game_state.mothership.max_crew
        self.crew_label.config(text=f"Crew: {crew}/{max_crew}")
        
        power = self.game_state.mothership.power_usage
        max_power = self.game_state.mothership.power_generation
        self.power_label.config(text=f"Power: {power}/{max_power}")
        
        # Update modules
        for module_id, module in self.game_state.mothership.modules.items():
            widgets = self.module_widgets[module_id]
            
            # Update upgrade progress
            if module.upgrade_start:
                progress = self.calculate_upgrade_progress(module)
                widgets['progress'].set(progress * 100)
                
                remaining = self.calculate_remaining_time(module)
                if remaining:
                    widgets['time'].config(
                        text=f"Time remaining: {str(remaining).split('.')[0]}"
                    )
                else:
                    self.complete_module_upgrade(module)
        
        # Update status bar
        if self.game_state.is_traveling:
            progress = self.game_state.travel_progress
            destination = self.game_state.travel_destination.name
            eta = self.game_state.travel_eta - now
            if eta.total_seconds() > 0:
                self.status_bar.config(
                    text=f"Traveling to {destination} - "
                    f"ETA: {str(eta).split('.')[0]} - "
                    f"Progress: {progress*100:.1f}%"
                )
            else:
                self.game_state.complete_travel()
                self.status_bar.config(text=f"Arrived at {destination}")
        else:
            self.status_bar.config(
                text=f"Current location: {self.game_state.current_region.name}"
            )
        
        # Schedule next update
        self.after(100, self.update_displays)
    
    def run(self):
        """Run the main window"""
        self.mainloop() 