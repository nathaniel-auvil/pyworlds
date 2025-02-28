import tkinter as tk
from tkinter import ttk

class ModuleInfoPopup(tk.Toplevel):
    def __init__(self, parent, module):
        super().__init__(parent)
        self.title(f"{module.name} Information")
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
        
        # Module type
        ttk.Label(self.scrollable_frame, text=f"Type: {module.module_type}", 
                 font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W, pady=5)
        
        # Current level
        ttk.Label(self.scrollable_frame, text=f"Current Level: {module.level}",
                 font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W, pady=5)
        
        # Power and crew requirements
        ttk.Label(self.scrollable_frame, text="Power Usage:", 
                 font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W, pady=(10,0))
        for level in range(1, module.level + 5):
            module.level = level  # Temporarily change level
            ttk.Label(self.scrollable_frame, 
                     text=f"Level {level}: {int(module.power_usage())}").pack(anchor=tk.W)
        module.level = module.level - 5  # Restore level
        
        ttk.Label(self.scrollable_frame, text="Crew Required:", 
                 font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W, pady=(10,0))
        for level in range(1, module.level + 5):
            module.level = level  # Temporarily change level
            ttk.Label(self.scrollable_frame, 
                     text=f"Level {level}: {module.crew_required()}").pack(anchor=tk.W)
        module.level = module.level - 5  # Restore level
        
        # Production/Collection rates if applicable
        if hasattr(module, 'collection_rate'):
            ttk.Label(self.scrollable_frame, text="Collection Rate:", 
                     font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W, pady=(10,0))
            for level in range(1, module.level + 5):
                module.level = level  # Temporarily change level
                ttk.Label(self.scrollable_frame, 
                         text=f"Level {level}: {int(module.collection_rate())}/hour").pack(anchor=tk.W)
            module.level = module.level - 5  # Restore level
        
        elif hasattr(module, 'production_rate'):
            ttk.Label(self.scrollable_frame, text="Production Rate:", 
                     font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W, pady=(10,0))
            for level in range(1, module.level + 5):
                module.level = level  # Temporarily change level
                ttk.Label(self.scrollable_frame, 
                         text=f"Level {level}: {int(module.production_rate())}/hour").pack(anchor=tk.W)
            module.level = module.level - 5  # Restore level
        
        elif hasattr(module, 'capacity'):
            ttk.Label(self.scrollable_frame, text="Storage Capacity:", 
                     font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W, pady=(10,0))
            for level in range(1, module.level + 5):
                module.level = level  # Temporarily change level
                ttk.Label(self.scrollable_frame, 
                         text=f"Level {level}: {module.capacity()}").pack(anchor=tk.W)
            module.level = module.level - 5  # Restore level
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=5) 