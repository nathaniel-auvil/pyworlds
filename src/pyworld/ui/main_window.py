import tkinter as tk
from tkinter import ttk
import time
from datetime import datetime, timedelta

from ..models.game_state import GameState
from .module_info import ModuleInfoPopup
from .station_view import StationView

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Space Empire")
        self.root.geometry("1024x768")
        
        self.game_state = GameState()
        
        self.create_gui()
        self.create_menu_bar()
        
    def create_gui(self):
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Top status bar
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Credits display
        self.credits_label = ttk.Label(self.status_frame, text=f"Credits: {self.game_state.credits}")
        self.credits_label.pack(side=tk.LEFT, padx=5)
        
        # Game speed indicator
        self.speed_label = ttk.Label(self.status_frame, text="Game Speed: 1.0x")
        self.speed_label.pack(side=tk.RIGHT, padx=5)

        # Create notebook for different views
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Mothership view
        self.mothership_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.mothership_frame, text="Mothership")
        self.create_mothership_view()
        
        # Station view
        self.station_view = StationView(self.notebook, self.game_state)
        self.notebook.add(self.station_view, text="Space Station")

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

    def create_mothership_view(self):
        # Resources display
        self.create_resource_display()
        
        # Ship status
        self.create_ship_status()
        
        # Modules display
        self.create_modules_display()

    def create_resource_display(self):
        self.resource_frame = ttk.LabelFrame(self.mothership_frame, text="Resources", padding="5")
        self.resource_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.resource_labels = {}
        resources = ['metal', 'gas', 'energy', 'refined_metal', 'refined_gas']
        for i, resource in enumerate(resources):
            # Resource name
            ttk.Label(self.resource_frame, text=f"{resource.replace('_', ' ').title()}:").grid(
                row=i//3, column=(i%3)*2, padx=(10,2), pady=2
            )
            
            # Resource amount
            self.resource_labels[resource] = ttk.Label(self.resource_frame, text="0")
            self.resource_labels[resource].grid(
                row=i//3, column=(i%3)*2+1, padx=(2,10), pady=2
            )

    def create_ship_status(self):
        self.status_frame = ttk.LabelFrame(self.mothership_frame, text="Ship Status", padding="5")
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Crew info
        ttk.Label(self.status_frame, text="Crew:").grid(row=0, column=0, padx=5)
        self.crew_label = ttk.Label(
            self.status_frame, 
            text=f"{self.game_state.mothership.current_crew}/{self.game_state.mothership.max_crew}"
        )
        self.crew_label.grid(row=0, column=1, padx=5)
        
        # Power info
        ttk.Label(self.status_frame, text="Power:").grid(row=0, column=2, padx=5)
        self.power_label = ttk.Label(
            self.status_frame,
            text=f"{self.game_state.mothership.power_generation}/{self.game_state.mothership.max_power}"
        )
        self.power_label.grid(row=0, column=3, padx=5)

    def create_modules_display(self):
        self.modules_frame = ttk.LabelFrame(self.mothership_frame, text="Ship Modules", padding="5")
        self.modules_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        self.module_info = {}
        for i, (module_id, module) in enumerate(self.game_state.mothership.modules.items()):
            frame = ttk.Frame(self.modules_frame)
            frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2)
            
            # Module name
            name = module.name
            module_label = ttk.Label(frame, text=f"{name}")
            module_label.grid(row=0, column=0, padx=10)
            
            # Info button
            info_btn = ttk.Button(frame, text="ℹ️", width=3,
                              command=lambda m=module: self.show_module_info(m))
            info_btn.grid(row=0, column=1, padx=2)
            
            # Level
            level_label = ttk.Label(frame, text=f"Level: {module.level}")
            level_label.grid(row=0, column=2, padx=5)
            
            # Status (active/inactive)
            status_var = tk.BooleanVar(value=module.is_active)
            status_check = ttk.Checkbutton(
                frame, text="Active", variable=status_var,
                command=lambda m=module, v=status_var: self.toggle_module(m, v)
            )
            status_check.grid(row=0, column=3, padx=5)
            
            # Power usage
            power_label = ttk.Label(frame, text=f"Power: {int(module.power_usage())}")
            power_label.grid(row=0, column=4, padx=5)
            
            # Crew requirement
            crew_label = ttk.Label(frame, text=f"Crew: {module.crew_required()}")
            crew_label.grid(row=0, column=5, padx=5)
            
            # Production/Collection rate if applicable
            rate_label = None
            if hasattr(module, 'collection_rate'):
                rate = module.collection_rate()
                rate_label = ttk.Label(frame, text=f"Rate: {int(rate)}/h")
                rate_label.grid(row=0, column=6, padx=5)
            elif hasattr(module, 'production_rate'):
                rate = module.production_rate()
                rate_label = ttk.Label(frame, text=f"Rate: {int(rate)}/h")
                rate_label.grid(row=0, column=6, padx=5)
            
            # Upgrade button
            upgrade_btn = ttk.Button(frame, text="Upgrade",
                                   command=lambda m=module_id: self.upgrade_module(m))
            upgrade_btn.grid(row=0, column=7, padx=5)
            
            self.module_info[module_id] = {
                'level_label': level_label,
                'power_label': power_label,
                'crew_label': crew_label,
                'rate_label': rate_label,
                'status_check': status_check,
                'upgrade_button': upgrade_btn
            }

    def toggle_module(self, module, status_var):
        """Toggle module active status"""
        if status_var.get():  # Trying to activate
            if module.can_activate(self.game_state.mothership):
                module.is_active = True
            else:
                status_var.set(False)  # Revert checkbox
                # Show error message
                tk.messagebox.showerror(
                    "Cannot Activate",
                    "Insufficient power or crew to activate this module!"
                )
        else:  # Deactivating
            module.is_active = False
        
        self.update_status_displays()

    def upgrade_module(self, module_id):
        """Upgrade a module"""
        # To be implemented
        pass

    def show_module_info(self, module):
        """Show detailed module information"""
        ModuleInfoPopup(self.root, module)

    def update_displays(self):
        """Update all displays"""
        # Update resources
        for resource, label in self.resource_labels.items():
            label.config(text=f"{int(self.game_state.mothership.resources[resource])}")
        
        # Update credits
        self.credits_label.config(text=f"Credits: {self.game_state.credits}")
        
        self.update_status_displays()
        
        # Schedule next update
        self.root.after(1000, self.update_displays)

    def update_status_displays(self):
        """Update ship status displays"""
        ship = self.game_state.mothership
        
        # Update crew display
        self.crew_label.config(
            text=f"{ship.current_crew}/{ship.max_crew} "
                f"(Available: {ship.available_crew})"
        )
        
        # Update power display
        self.power_label.config(
            text=f"{ship.power_generation}/{ship.max_power} "
                f"(Available: {int(ship.available_power)})"
        )
        
        # Update module displays
        for module_id, module in ship.modules.items():
            info = self.module_info[module_id]
            info['power_label'].config(text=f"Power: {int(module.power_usage())}")
            info['crew_label'].config(text=f"Crew: {module.crew_required()}")
            
            if info['rate_label']:
                if hasattr(module, 'collection_rate'):
                    rate = module.collection_rate()
                    info['rate_label'].config(text=f"Rate: {int(rate)}/h")
                elif hasattr(module, 'production_rate'):
                    rate = module.production_rate()
                    info['rate_label'].config(text=f"Rate: {int(rate)}/h")

    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Game speed submenu
        speed_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Game Speed", menu=speed_menu)
        
        # Add speed options
        speeds = [0.5, 1.0, 2.0, 5.0, 10.0, 50.0]
        for speed in speeds:
            speed_menu.add_radiobutton(
                label=f"{speed}x",
                value=speed,
                variable=tk.DoubleVar(value=self.game_state.game_speed),
                command=lambda s=speed: self.set_game_speed(s)
            )

    def set_game_speed(self, speed):
        self.game_state.game_speed = speed
        self.speed_label.config(text=f"Game Speed: {speed}x")

    def run(self):
        self.update_displays()
        self.root.mainloop() 