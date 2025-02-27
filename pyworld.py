import tkinter as tk
from tkinter import ttk
import time
import json
from datetime import datetime, timedelta

class BuildingInfoPopup(tk.Toplevel):
    def __init__(self, parent, building_name, building_data):
        super().__init__(parent)
        self.title(f"{building_name.replace('_', ' ').title()} Information")
        self.geometry("400x500")
        
        # Make the popup modal
        self.transient(parent)
        self.grab_set()
        
        # Create scrollable frame
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Headers
        ttk.Label(self.scrollable_frame, text="Level", font=('TkDefaultFont', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(self.scrollable_frame, text="Production/Capacity", font=('TkDefaultFont', 10, 'bold')).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.scrollable_frame, text="Upgrade Cost", font=('TkDefaultFont', 10, 'bold')).grid(row=0, column=2, padx=5, pady=5)
        ttk.Separator(self.scrollable_frame, orient='horizontal').grid(row=1, column=0, columnspan=3, sticky='ew', pady=5)
        
        # Calculate and display info for each level
        max_level = 15 if 'mine' in building_name else 50
        current_level = building_data['level']
        
        for level in range(1, max_level + 1):
            row = level + 1
            
            # Level number
            level_text = f"{level}"
            if level == current_level:
                level_text += " (Current)"
            ttk.Label(self.scrollable_frame, text=level_text).grid(row=row, column=0, padx=5, pady=2)
            
            # Production/Capacity
            if 'base_production' in building_data:
                prod = building_data['base_production'] * (1.25 ** (level - 1))
                ttk.Label(self.scrollable_frame, text=f"{int(prod)}/hour").grid(row=row, column=1, padx=5, pady=2)
            elif 'base_capacity' in building_data:
                capacity = building_data['base_capacity'] * level
                ttk.Label(self.scrollable_frame, text=f"{capacity}").grid(row=row, column=1, padx=5, pady=2)
            else:
                ttk.Label(self.scrollable_frame, text="-").grid(row=row, column=1, padx=5, pady=2)
            
            # Upgrade cost
            base_cost = building_data['cost']
            level_cost = {
                resource: int(amount * (1.5 ** (level - 1)))
                for resource, amount in base_cost.items()
            }
            cost_text = f"M: {level_cost['metal']}, C: {level_cost['crystal']}"
            ttk.Label(self.scrollable_frame, text=cost_text).grid(row=row, column=2, padx=5, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=5)

class SpaceEmpire:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Space Empire")
        self.root.geometry("1024x768")
        
        # Game settings
        self.game_speed = 1.0  # Default speed multiplier
        
        # Create menu bar
        self.create_menu_bar()
        
        # Game state
        self.resources = {
            'metal': 500,
            'crystal': 300,
            'energy': 100,
            'last_update': datetime.now().timestamp()   
        }
        
        # Storage capacities
        self.storage = {
            'metal': 1000,
            'crystal': 1000
        }
        
        self.buildings = {
            'metal_mine': {
                'level': 1, 
                'base_production': 10,
                'production': 10,
                'cost': {'metal': 60, 'crystal': 15},
                'build_time': 60,  # Base build time in seconds
                'current_build': None  # Will store build info when upgrading
            },
            'crystal_mine': {
                'level': 1, 
                'base_production': 8,
                'production': 8,
                'cost': {'metal': 48, 'crystal': 24},
                'build_time': 80,
                'current_build': None
            },
            'solar_plant': {
                'level': 1, 
                'base_production': 20,
                'production': 20,
                'cost': {'metal': 75, 'crystal': 30},
                'build_time': 100,
                'current_build': None
            },
            'storage_facility': {
                'level': 1,
                'base_capacity': 1000,
                'cost': {'metal': 100, 'crystal': 50},
                'build_time': 120,
                'current_build': None
            },
            'shipyard': {
                'level': 0, 
                'cost': {'metal': 400, 'crystal': 200},
                'build_time': 300,
                'current_build': None
            },
            'research_lab': {
                'level': 0, 
                'cost': {'metal': 200, 'crystal': 400},
                'build_time': 240,
                'current_build': None
            }
        }

        self.create_gui()
        
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
                capacity_label = ttk.Label(self.resource_frame, text=f"/ {self.storage[resource]}")
                capacity_label.grid(row=0, column=i*4+3, padx=5)
                self.resource_labels[f"{resource}_capacity"] = capacity_label

        # Buildings frame
        self.buildings_frame = ttk.LabelFrame(self.main_frame, text="Buildings", padding="5")
        self.buildings_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Create building buttons
        self.building_info = {}
        for i, (building, data) in enumerate(self.buildings.items()):
            frame = ttk.Frame(self.buildings_frame)
            frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2)
            
            name = building.replace('_', ' ').title()
            building_label = ttk.Label(frame, text=f"{name}")
            building_label.grid(row=0, column=0, padx=5)
            
            # Add info button
            info_btn = ttk.Button(frame, text="ℹ️", width=3,
                                command=lambda b=building, d=data: self.show_building_info(b, d))
            info_btn.grid(row=0, column=1, padx=2)
            
            level_label = ttk.Label(frame, text=f"Level: {data['level']}")
            level_label.grid(row=0, column=2, padx=5)
            
            # Production/Storage info
            if 'production' in data:
                prod_label = ttk.Label(frame, text=f"Production: {data['production']}/h")
                prod_label.grid(row=0, column=3, padx=5)
            elif building == 'storage_facility':
                prod_label = ttk.Label(frame, text=f"Capacity: {data['base_capacity'] * data['level']}")
                prod_label.grid(row=0, column=3, padx=5)
            else:
                prod_label = None
            
            cost_text = f"Cost: {data['cost']['metal']}M, {data['cost']['crystal']}C"
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
                                   command=lambda b=building: self.upgrade_building(b))
            upgrade_btn.grid(row=0, column=7, padx=5)
            
            self.building_info[building] = {
                'level_label': level_label,
                'production_label': prod_label,
                'cost_label': cost_label,
                'upgrade_button': upgrade_btn,
                'progress_var': progress_var,
                'progress_bar': progress_bar,
                'time_label': time_label
            }

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

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
                variable=tk.DoubleVar(value=self.game_speed),
                command=lambda s=speed: self.set_game_speed(s)
            )

    def set_game_speed(self, speed):
        self.game_speed = speed
        self.speed_label.config(text=f"Game Speed: {speed}x")
        self.update_production_displays()
    
    def update_production_displays(self):
        for resource in ['metal', 'crystal']:
            mine = f"{resource}_mine"
            production = self.buildings[mine]['production'] * self.buildings[mine]['level'] * self.game_speed
            self.resource_labels[f"{resource}_rate"].config(text=f"(+{int(production)}/h)")
            
            if 'production' in self.buildings[mine]:
                self.building_info[mine]['production_label'].config(
                    text=f"Production: {int(production)}/h"
                )
        
        # Update solar plant display
        solar_production = self.buildings['solar_plant']['production'] * self.buildings['solar_plant']['level'] * self.game_speed
        self.building_info['solar_plant']['production_label'].config(
            text=f"Production: {int(solar_production)}/h"
        )

    def update_resources(self):
        current_time = datetime.now().timestamp()
        elapsed_time = (current_time - self.resources['last_update']) / 3600  # Convert to hours
        
        # Apply game speed multiplier to elapsed time
        elapsed_time *= self.game_speed
        
        # Calculate production
        for resource in ['metal', 'crystal']:
            mine = f"{resource}_mine"
            production = self.buildings[mine]['production'] * self.buildings[mine]['level'] * elapsed_time
            
            # Check storage capacity
            available_storage = self.storage[resource] - self.resources[resource]
            production = min(production, available_storage)
            
            self.resources[resource] += production
        
        self.resources['energy'] = self.buildings['solar_plant']['production'] * self.buildings['solar_plant']['level']
        
        # Update display
        for resource in ['metal', 'crystal', 'energy']:
            self.resource_labels[resource].config(text=f"{int(self.resources[resource])}")
        
        self.resources['last_update'] = current_time
        
        # Update building progress
        self.update_building_progress()
        
        # Schedule next update
        self.root.after(1000, self.update_resources)  # Update every second

    def update_building_progress(self):
        current_time = datetime.now()
        
        for building, data in self.buildings.items():
            if data['current_build']:
                start_time = data['current_build']['start_time']
                end_time = data['current_build']['end_time']
                total_seconds = (end_time - start_time).total_seconds()
                elapsed_seconds = (current_time - start_time).total_seconds()
                
                if current_time >= end_time:
                    # Complete the upgrade
                    self.complete_upgrade(building)
                else:
                    # Update progress bar and time remaining
                    progress = (elapsed_seconds / total_seconds) * 100
                    self.building_info[building]['progress_var'].set(progress)
                    
                    remaining = end_time - current_time
                    remaining_str = str(timedelta(seconds=int(remaining.total_seconds())))
                    self.building_info[building]['time_label'].config(text=f"Time: {remaining_str}")

    def complete_upgrade(self, building):
        data = self.buildings[building]
        data['level'] += 1
        data['current_build'] = None
        
        # Update production rates and storage capacity
        if 'base_production' in data:
            data['production'] = data['base_production'] * (1.25 ** (data['level'] - 1))
            self.building_info[building]['production_label'].config(
                text=f"Production: {int(data['production'])}/h"
            )
        elif building == 'storage_facility':
            for resource in ['metal', 'crystal']:
                self.storage[resource] = data['base_capacity'] * data['level']
                self.resource_labels[f"{resource}_capacity"].config(
                    text=f"/ {self.storage[resource]}"
                )
            self.building_info[building]['production_label'].config(
                text=f"Capacity: {data['base_capacity'] * data['level']}"
            )
        
        # Update level display
        self.building_info[building]['level_label'].config(text=f"Level: {data['level']}")
        
        # Reset progress bar and time label
        self.building_info[building]['progress_var'].set(0)
        self.building_info[building]['time_label'].config(text="")
        
        # Update costs for next level
        for resource, amount in data['cost'].items():
            data['cost'][resource] = int(amount * 1.5)
        
        cost_text = f"Cost: {data['cost']['metal']}M, {data['cost']['crystal']}C"
        self.building_info[building]['cost_label'].config(text=cost_text)
        
        # Re-enable upgrade button
        self.building_info[building]['upgrade_button'].config(state='normal')

    def show_building_info(self, building_name, building_data):
        BuildingInfoPopup(self.root, building_name, building_data)

    def upgrade_building(self, building):
        data = self.buildings[building]
        cost = data['cost']
        
        # Check level cap
        max_level = 15 if 'mine' in building else 50
        if data['level'] >= max_level:
            return
        
        # Check if we can afford it
        if (self.resources['metal'] >= cost['metal'] and 
            self.resources['crystal'] >= cost['crystal']):
            
            # Check if any building is currently under construction
            for b in self.buildings.values():
                if b['current_build'] is not None:
                    return  # Can't build if something is already under construction
            
            # Deduct resources
            self.resources['metal'] -= cost['metal']
            self.resources['crystal'] -= cost['crystal']
            
            # Calculate build time (increases with level)
            build_time = data['build_time'] * (1.2 ** data['level'])
            
            # Apply game speed to build time
            build_time /= self.game_speed
            
            # Set up the build
            start_time = datetime.now()
            end_time = start_time + timedelta(seconds=build_time)
            
            data['current_build'] = {
                'start_time': start_time,
                'end_time': end_time
            }
            
            # Disable upgrade button during construction
            self.building_info[building]['upgrade_button'].config(state='disabled')

    def run(self):
        self.update_resources()
        self.root.mainloop()

if __name__ == "__main__":
    game = SpaceEmpire()
    game.run()
