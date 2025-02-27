import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

from ..models.game_state import GameState
from .building_info import BuildingInfoPopup

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
        
        # Game speed indicator
        self.speed_label = ttk.Label(self.status_frame, text="Game Speed: 1.0x")
        self.speed_label.pack(side=tk.RIGHT, padx=5)

        # Resources display
        self.create_resource_display()
        
        # Buildings display
        self.create_buildings_display()

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)

    def create_resource_display(self):
        self.resource_frame = ttk.LabelFrame(self.main_frame, text="Resources", padding="5")
        self.resource_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.resource_labels = {}
        for i, resource in enumerate(['metal', 'crystal', 'energy']):
            ttk.Label(self.resource_frame, text=f"{resource.title()}:").grid(row=0, column=i*4, padx=5)
            self.resource_labels[resource] = ttk.Label(self.resource_frame, text="0")
            self.resource_labels[resource].grid(row=0, column=i*4+1, padx=5)
            
            # Add production rate display
            if resource != 'energy':
                rate_label = ttk.Label(self.resource_frame, text="(+0/h)")
                rate_label.grid(row=0, column=i*4+2, padx=5)
                self.resource_labels[f"{resource}_rate"] = rate_label
            
            if resource != 'energy':
                capacity_label = ttk.Label(self.resource_frame, text=f"/ {self.game_state.storage[resource]}")
                capacity_label.grid(row=0, column=i*4+3, padx=5)
                self.resource_labels[f"{resource}_capacity"] = capacity_label

    def create_buildings_display(self):
        self.buildings_frame = ttk.LabelFrame(self.main_frame, text="Buildings", padding="5")
        self.buildings_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        self.building_info = {}
        for i, (building_name, building) in enumerate(self.game_state.buildings.items()):
            frame = ttk.Frame(self.buildings_frame)
            frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2)
            
            name = building_name.replace('_', ' ').title()
            building_label = ttk.Label(frame, text=f"{name}")
            building_label.grid(row=0, column=0, padx=5)
            
            # Add info button
            info_btn = ttk.Button(frame, text="ℹ️", width=3,
                                command=lambda b=building: self.show_building_info(b))
            info_btn.grid(row=0, column=1, padx=2)
            
            level_label = ttk.Label(frame, text=f"Level: {building.level}")
            level_label.grid(row=0, column=2, padx=5)
            
            # Production/Storage info
            if building.base_production is not None:
                prod_label = ttk.Label(frame, text=f"Production: {int(building.calculate_production())}/h")
                prod_label.grid(row=0, column=3, padx=5)
            elif building_name == 'storage_facility':
                prod_label = ttk.Label(frame, text=f"Capacity: {building.calculate_capacity()}")
                prod_label.grid(row=0, column=3, padx=5)
            else:
                prod_label = None
            
            cost_text = f"Cost: {building.calculate_cost()['metal']}M, {building.calculate_cost()['crystal']}C"
            cost_label = ttk.Label(frame, text=cost_text)
            cost_label.grid(row=0, column=4, padx=5)
            
            # Progress bar for building
            progress_var = tk.DoubleVar(value=0)
            progress_bar = ttk.Progressbar(frame, length=100, mode='determinate', variable=progress_var)
            progress_bar.grid(row=0, column=5, padx=5)
            
            # Time remaining label
            time_label = ttk.Label(frame, text="")
            time_label.grid(row=0, column=6, padx=5)
            
            upgrade_btn = ttk.Button(frame, text="Upgrade", 
                                   command=lambda b=building_name: self.upgrade_building(b))
            upgrade_btn.grid(row=0, column=7, padx=5)
            
            self.building_info[building_name] = {
                'level_label': level_label,
                'production_label': prod_label,
                'cost_label': cost_label,
                'upgrade_button': upgrade_btn,
                'progress_var': progress_var,
                'progress_bar': progress_bar,
                'time_label': time_label
            }

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
        self.update_production_displays()
    
    def update_production_displays(self):
        for resource in ['metal', 'crystal']:
            mine = f"{resource}_mine"
            building = self.game_state.buildings[mine]
            production = building.calculate_production() * self.game_state.game_speed
            self.resource_labels[f"{resource}_rate"].config(text=f"(+{int(production)}/h)")
            
            if building.base_production is not None:
                self.building_info[mine]['production_label'].config(
                    text=f"Production: {int(production)}/h"
                )
        
        # Update solar plant display
        solar_plant = self.game_state.buildings['solar_plant']
        solar_production = solar_plant.calculate_production() * self.game_state.game_speed
        self.building_info['solar_plant']['production_label'].config(
            text=f"Production: {int(solar_production)}/h"
        )

    def update_resources(self):
        current_time = datetime.now().timestamp()
        elapsed_time = (current_time - self.game_state.resources['last_update']) / 3600  # Convert to hours
        
        self.game_state.update_resources(elapsed_time)
        
        # Update display
        for resource in ['metal', 'crystal', 'energy']:
            self.resource_labels[resource].config(text=f"{int(self.game_state.resources[resource])}")
        
        # Update building progress
        self.update_building_progress()
        
        # Schedule next update
        self.root.after(1000, self.update_resources)  # Update every second

    def update_building_progress(self):
        current_time = datetime.now()
        
        for building_name, building in self.game_state.buildings.items():
            if building.current_build:
                start_time = building.current_build['start_time']
                end_time = building.current_build['end_time']
                total_seconds = (end_time - start_time).total_seconds()
                elapsed_seconds = (current_time - start_time).total_seconds()
                
                if current_time >= end_time:
                    # Complete the upgrade
                    self.complete_upgrade(building_name)
                else:
                    # Update progress bar and time remaining
                    progress = (elapsed_seconds / total_seconds) * 100
                    self.building_info[building_name]['progress_var'].set(progress)
                    
                    remaining = end_time - current_time
                    remaining_str = str(timedelta(seconds=int(remaining.total_seconds())))
                    self.building_info[building_name]['time_label'].config(text=f"Time: {remaining_str}")

    def complete_upgrade(self, building_name):
        building = self.game_state.buildings[building_name]
        building.level += 1
        building.current_build = None
        
        # Update production rates and storage capacity
        if building.base_production is not None:
            building.production = building.calculate_production()
            self.building_info[building_name]['production_label'].config(
                text=f"Production: {int(building.production)}/h"
            )
        elif building_name == 'storage_facility':
            self.game_state.update_storage_capacity()
            for resource in ['metal', 'crystal']:
                self.resource_labels[f"{resource}_capacity"].config(
                    text=f"/ {self.game_state.storage[resource]}"
                )
            self.building_info[building_name]['production_label'].config(
                text=f"Capacity: {building.calculate_capacity()}"
            )
        
        # Update level display
        self.building_info[building_name]['level_label'].config(text=f"Level: {building.level}")
        
        # Reset progress bar and time label
        self.building_info[building_name]['progress_var'].set(0)
        self.building_info[building_name]['time_label'].config(text="")
        
        # Update costs display
        cost_text = f"Cost: {building.calculate_cost()['metal']}M, {building.calculate_cost()['crystal']}C"
        self.building_info[building_name]['cost_label'].config(text=cost_text)
        
        # Re-enable upgrade button
        self.building_info[building_name]['upgrade_button'].config(state='normal')
        
        # Update production displays to reflect new rates
        self.update_production_displays()

    def upgrade_building(self, building_name):
        building = self.game_state.buildings[building_name]
        costs = building.calculate_cost()
        
        # Check level cap
        max_level = 15 if 'mine' in building_name else 50
        if building.level >= max_level:
            return
        
        # Check if we can afford it
        if self.game_state.can_afford(costs):
            # Check if any building is currently under construction
            for b in self.game_state.buildings.values():
                if b.current_build is not None:
                    return  # Can't build if something is already under construction
            
            # Deduct resources
            self.game_state.deduct_resources(costs)
            
            # Calculate build time (increases with level)
            build_time = building.calculate_build_time() / self.game_state.game_speed
            
            # Set up the build
            start_time = datetime.now()
            end_time = start_time + timedelta(seconds=build_time)
            
            building.current_build = {
                'start_time': start_time,
                'end_time': end_time
            }
            
            # Disable upgrade button during construction
            self.building_info[building_name]['upgrade_button'].config(state='disabled')

    def show_building_info(self, building):
        BuildingInfoPopup(self.root, building)

    def run(self):
        self.update_resources()
        self.root.mainloop() 