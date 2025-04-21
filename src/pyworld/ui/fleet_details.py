import tkinter as tk
from tkinter import ttk
from datetime import datetime

class FleetDetailsDialog(tk.Toplevel):
    def __init__(self, parent, fleet):
        super().__init__(parent)
        self.fleet = fleet
        self.title(f"Fleet Details - {fleet.name}")
        self.geometry("600x600")
        
        # Make the dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Create main container with grid layout
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_container.grid_rowconfigure(0, weight=1)  # Make content area expand
        main_container.grid_columnconfigure(0, weight=1)
        
        # Create scrollable frame
        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Ship Information
        self.create_ship_info()
        
        # Resource Information
        self.create_resource_info()
        
        # Equipment Information
        self.create_equipment_info()
        
        # Upgrade Information
        self.create_upgrade_info()
        
        # Pack canvas and scrollbar in grid
        canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Close button at the bottom
        ttk.Button(main_container, text="Close", command=self.destroy).grid(row=1, column=0, columnspan=2, pady=10, sticky='ew')
        
        # Start update loop
        self.update_displays()
    
    def create_ship_info(self):
        """Create the ship information section"""
        frame = ttk.LabelFrame(self.scrollable_frame, text="Ship Information", padding="10")
        frame.pack(fill='x', pady=5)
        
        # Configure grid
        frame.grid_columnconfigure(1, weight=1)
        
        # Ship type and level
        ttk.Label(frame, text="Type:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(frame, text=self.fleet.ship_type).grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(frame, text="Level:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.level_label = ttk.Label(frame, text=str(self.fleet.level))
        self.level_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Location
        ttk.Label(frame, text="Location:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.location_label = ttk.Label(frame, text=self.fleet.current_location)
        self.location_label.grid(row=2, column=1, sticky='w', padx=5, pady=2)
        
        # Travel status
        self.travel_label = ttk.Label(frame, text="")
        self.travel_label.grid(row=3, column=0, columnspan=2, sticky='w', padx=5, pady=2)
    
    def create_resource_info(self):
        """Create the resource information section"""
        frame = ttk.LabelFrame(self.scrollable_frame, text="Resources", padding="10")
        frame.pack(fill='x', pady=5)
        
        # Configure grid
        frame.grid_columnconfigure(1, weight=1)
        
        # Storage capacity
        ttk.Label(frame, text="Storage:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.storage_label = ttk.Label(
            frame,
            text=f"{self.fleet.storage_used}/{self.fleet.storage_capacity}"
        )
        self.storage_label.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # Resource amounts
        self.resource_labels = {}
        row = 1
        for resource in ['metal', 'gas', 'energy', 'refined_metal', 'refined_gas']:
            ttk.Label(frame, text=f"{resource.replace('_', ' ').title()}:").grid(
                row=row, column=0, sticky='w', padx=5, pady=2
            )
            label = ttk.Label(
                frame,
                text=str(self.fleet.resources.get(resource, 0))
            )
            label.grid(row=row, column=1, sticky='w', padx=5, pady=2)
            self.resource_labels[resource] = label
            row += 1
    
    def create_equipment_info(self):
        """Create the equipment information section"""
        frame = ttk.LabelFrame(self.scrollable_frame, text="Equipment", padding="10")
        frame.pack(fill='x', pady=5)
        
        # Configure grid
        frame.grid_columnconfigure(1, weight=1)
        
        # Mining drones
        ttk.Label(frame, text="Mining Drones:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.drones_label = ttk.Label(
            frame,
            text=f"{self.fleet.mining_drones}/{self.fleet.max_drones}"
        )
        self.drones_label.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # Gas collectors
        ttk.Label(frame, text="Gas Collectors:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.collectors_label = ttk.Label(
            frame,
            text=f"{self.fleet.gas_collectors}/{self.fleet.max_collectors}"
        )
        self.collectors_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)
    
    def create_upgrade_info(self):
        """Create the upgrade information section"""
        frame = ttk.LabelFrame(self.scrollable_frame, text="Upgrade Status", padding="10")
        frame.pack(fill='x', pady=5)
        
        # Configure grid
        frame.grid_columnconfigure(1, weight=1)
        
        # Upgrade progress
        self.upgrade_progress = ttk.Progressbar(
            frame,
            mode='determinate',
            length=400
        )
        self.upgrade_progress.grid(row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=2)
        
        self.upgrade_label = ttk.Label(frame, text="")
        self.upgrade_label.grid(row=1, column=0, columnspan=2, sticky='w', padx=5, pady=2)
    
    def update_displays(self):
        """Update all displays"""
        # Update ship info
        self.level_label.config(text=f"Level: {self.fleet.level}")
        self.location_label.config(text=f"Location: {self.fleet.current_location}")
        
        # Update travel status
        if self.fleet.is_traveling:
            remaining = self.fleet.travel_end - datetime.now()
            if remaining.total_seconds() > 0:
                self.travel_label.config(
                    text=f"Traveling to {self.fleet.destination} - "
                         f"ETA: {str(remaining).split('.')[0]}"
                )
            else:
                self.travel_label.config(text="")
        else:
            self.travel_label.config(text="")
        
        # Update resource info
        self.storage_label.config(
            text=f"Storage Used: {self.fleet.storage_used}/{self.fleet.storage_capacity}"
        )
        
        for resource, label in self.resource_labels.items():
            label.config(
                text=f"{resource.replace('_', ' ').title()}: "
                     f"{self.fleet.resources.get(resource, 0)}"
            )
        
        # Update equipment info
        self.drones_label.config(
            text=f"Mining Drones: {self.fleet.mining_drones}/{self.fleet.max_drones}"
        )
        self.collectors_label.config(
            text=f"Gas Collectors: {self.fleet.gas_collectors}/{self.fleet.max_collectors}"
        )
        
        # Update upgrade progress
        if self.fleet.upgrade_start and self.fleet.upgrade_end:
            elapsed = datetime.now() - self.fleet.upgrade_start
            total = self.fleet.upgrade_end - self.fleet.upgrade_start
            progress = min(100, (elapsed.total_seconds() / total.total_seconds()) * 100)
            
            self.upgrade_progress['value'] = progress
            remaining = self.fleet.upgrade_end - datetime.now()
            if remaining.total_seconds() > 0:
                self.upgrade_label.config(
                    text=f"Time remaining: {str(remaining).split('.')[0]}"
                )
            else:
                self.upgrade_label.config(text="")
        else:
            self.upgrade_progress['value'] = 0
            self.upgrade_label.config(text="")
        
        # Schedule next update
        self.after(100, self.update_displays) 