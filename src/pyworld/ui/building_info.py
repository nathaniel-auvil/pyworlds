import tkinter as tk
from tkinter import ttk

class BuildingInfoPopup(tk.Toplevel):
    def __init__(self, parent, building):
        super().__init__(parent)
        self.title(f"{building.name.replace('_', ' ').title()} Information")
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
        max_level = 15 if 'mine' in building.name else 50
        current_level = building.level
        
        for level in range(1, max_level + 1):
            row = level + 1
            
            # Level number
            level_text = f"{level}"
            if level == current_level:
                level_text += " (Current)"
            ttk.Label(self.scrollable_frame, text=level_text).grid(row=row, column=0, padx=5, pady=2)
            
            # Production/Capacity
            if building.base_production is not None:
                prod = building.calculate_production(level)
                ttk.Label(self.scrollable_frame, text=f"{int(prod)}/hour").grid(row=row, column=1, padx=5, pady=2)
            elif building.base_capacity is not None:
                capacity = building.calculate_capacity(level)
                ttk.Label(self.scrollable_frame, text=f"{capacity}").grid(row=row, column=1, padx=5, pady=2)
            else:
                ttk.Label(self.scrollable_frame, text="-").grid(row=row, column=1, padx=5, pady=2)
            
            # Upgrade cost
            level_cost = building.calculate_cost(level)
            cost_text = f"M: {level_cost['metal']}, C: {level_cost['crystal']}"
            ttk.Label(self.scrollable_frame, text=cost_text).grid(row=row, column=2, padx=5, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=5) 