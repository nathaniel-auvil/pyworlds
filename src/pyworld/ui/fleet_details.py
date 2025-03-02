import tkinter as tk
from tkinter import ttk
from datetime import datetime

class FleetDetailsDialog(tk.Toplevel):
    def __init__(self, parent, fleet):
        super().__init__(parent)
        self.fleet = fleet
        self.title(f"Fleet Details - {fleet.name}")
        self.geometry("500x600")
        
        # Make the dialog modal
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
        
        # Ship Information
        self.create_ship_info()
        
        # Resource Information
        self.create_resource_info()
        
        # Equipment Information
        self.create_equipment_info()
        
        # Upgrade Information
        self.create_upgrade_info()
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=5)
        
        # Start update loop
        self.update_displays()
    
    def create_ship_info(self):
        """Create the ship information section"""
        frame = ttk.LabelFrame(self.scrollable_frame, text="Ship Information", padding="5")
        frame.pack(fill='x', pady=5)
        
        # Ship type and level
        ttk.Label(frame, text=f"Type: {self.fleet.ship_type}").pack(anchor='w')
        self.level_label = ttk.Label(frame, text=f"Level: {self.fleet.level}")
        self.level_label.pack(anchor='w')
        
        # Location
        self.location_label = ttk.Label(frame, text=f"Location: {self.fleet.current_location}")
        self.location_label.pack(anchor='w')
        
        # Travel status
        self.travel_label = ttk.Label(frame, text="")
        self.travel_label.pack(anchor='w')
    
    def create_resource_info(self):
        """Create the resource information section"""
        frame = ttk.LabelFrame(self.scrollable_frame, text="Resources", padding="5")
        frame.pack(fill='x', pady=5)
        
        # Storage capacity
        self.storage_label = ttk.Label(
            frame,
            text=f"Storage Used: {self.fleet.storage_used}/{self.fleet.storage_capacity}"
        )
        self.storage_label.pack(anchor='w')
        
        # Resource amounts
        self.resource_labels = {}
        for resource in ['metal', 'gas', 'energy', 'refined_metal', 'refined_gas']:
            label = ttk.Label(
                frame,
                text=f"{resource.replace('_', ' ').title()}: "
                     f"{self.fleet.resources.get(resource, 0)}"
            )
            label.pack(anchor='w')
            self.resource_labels[resource] = label
    
    def create_equipment_info(self):
        """Create the equipment information section"""
        frame = ttk.LabelFrame(self.scrollable_frame, text="Equipment", padding="5")
        frame.pack(fill='x', pady=5)
        
        # Mining drones
        self.drones_label = ttk.Label(
            frame,
            text=f"Mining Drones: {self.fleet.mining_drones}/{self.fleet.max_drones}"
        )
        self.drones_label.pack(anchor='w')
        
        # Gas collectors
        self.collectors_label = ttk.Label(
            frame,
            text=f"Gas Collectors: {self.fleet.gas_collectors}/{self.fleet.max_collectors}"
        )
        self.collectors_label.pack(anchor='w')
    
    def create_upgrade_info(self):
        """Create the upgrade information section"""
        frame = ttk.LabelFrame(self.scrollable_frame, text="Upgrade Status", padding="5")
        frame.pack(fill='x', pady=5)
        
        # Upgrade progress
        self.upgrade_frame = ttk.Frame(frame)
        self.upgrade_frame.pack(fill='x')
        
        self.upgrade_progress = ttk.Progressbar(
            self.upgrade_frame,
            mode='determinate',
            length=200
        )
        self.upgrade_progress.pack(side='left', padx=5)
        
        self.upgrade_label = ttk.Label(self.upgrade_frame, text="")
        self.upgrade_label.pack(side='left')
    
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