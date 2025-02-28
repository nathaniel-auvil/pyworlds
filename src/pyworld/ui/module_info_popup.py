import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

class ModuleInfoPopup(tk.Toplevel):
    def __init__(self, parent, module):
        super().__init__(parent)
        self.title(f"{module.name.replace('_', ' ').title()} Information")
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
        ttk.Label(
            self.scrollable_frame,
            text=module.module_type,
            font=('TkDefaultFont', 12, 'bold')
        ).pack(anchor='w', pady=5)
        
        # Current level
        ttk.Label(
            self.scrollable_frame,
            text=f"Current Level: {module.level}",
            font=('TkDefaultFont', 10, 'bold')
        ).pack(anchor='w', pady=5)
        
        # Power usage section
        ttk.Label(
            self.scrollable_frame,
            text="Power Usage:",
            font=('TkDefaultFont', 10, 'bold')
        ).pack(anchor='w', pady=5)
        
        # Store current level
        current_level = module.level
        
        # Show power usage for levels 1 through current + 4
        for level in range(1, current_level + 5):
            # Temporarily set module level
            module.level = level
            power = module.power_usage()
            
            text = f"Level {level}: {power} power"
            if level == current_level:
                text += " (current)"
            
            ttk.Label(self.scrollable_frame, text=text).pack(anchor='w', padx=20)
        
        # Crew requirements section
        ttk.Label(
            self.scrollable_frame,
            text="Crew Requirements:",
            font=('TkDefaultFont', 10, 'bold')
        ).pack(anchor='w', pady=5)
        
        # Show crew requirements for levels 1 through current + 4
        for level in range(1, current_level + 5):
            module.level = level
            crew = module.crew_required()
            
            text = f"Level {level}: {crew} crew"
            if level == current_level:
                text += " (current)"
            
            ttk.Label(self.scrollable_frame, text=text).pack(anchor='w', padx=20)
        
        # Production/Collection rates section
        if hasattr(module, 'collection_rate'):
            ttk.Label(
                self.scrollable_frame,
                text="Collection Rates:",
                font=('TkDefaultFont', 10, 'bold')
            ).pack(anchor='w', pady=5)
            
            for level in range(1, current_level + 5):
                module.level = level
                rate = module.collection_rate()
                
                text = f"Level {level}: {rate}/hour"
                if level == current_level:
                    text += " (current)"
                
                ttk.Label(self.scrollable_frame, text=text).pack(anchor='w', padx=20)
        
        elif hasattr(module, 'production_rate'):
            ttk.Label(
                self.scrollable_frame,
                text="Production Rates:",
                font=('TkDefaultFont', 10, 'bold')
            ).pack(anchor='w', pady=5)
            
            for level in range(1, current_level + 5):
                module.level = level
                rate = module.production_rate()
                
                text = f"Level {level}: {rate}/hour"
                if level == current_level:
                    text += " (current)"
                
                ttk.Label(self.scrollable_frame, text=text).pack(anchor='w', padx=20)
        
        elif hasattr(module, 'capacity'):
            ttk.Label(
                self.scrollable_frame,
                text="Storage Capacity:",
                font=('TkDefaultFont', 10, 'bold')
            ).pack(anchor='w', pady=5)
            
            for level in range(1, current_level + 5):
                module.level = level
                capacity = module.capacity()
                
                text = f"Level {level}: {capacity}"
                if level == current_level:
                    text += " (current)"
                
                ttk.Label(self.scrollable_frame, text=text).pack(anchor='w', padx=20)
        
        # Restore original level
        module.level = current_level
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=5) 