import tkinter as tk
from tkinter import ttk, messagebox
from datetime import timedelta
from typing import Dict, Optional

class RegionCanvas(tk.Canvas):
    def __init__(self, parent, region, **kwargs):
        super().__init__(parent, **kwargs)
        self.region = region
        self.cell_size = 50
        self.deposit_markers = {}
        self.bind('<Configure>', self.on_resize)
        
        # Calculate canvas size based on region size
        width = region.size[0] * self.cell_size
        height = region.size[1] * self.cell_size
        self.configure(width=width, height=height)
        
        self.draw_grid()
        self.draw_deposits()
    
    def on_resize(self, event):
        """Handle canvas resize"""
        self.cell_size = min(
            event.width // self.region.size[0],
            event.height // self.region.size[1]
        )
        self.draw_grid()
        self.draw_deposits()
    
    def draw_grid(self):
        """Draw the region grid"""
        self.delete('grid')
        width = self.region.size[0] * self.cell_size
        height = self.region.size[1] * self.cell_size
        
        # Draw vertical lines
        for i in range(self.region.size[0] + 1):
            x = i * self.cell_size
            self.create_line(x, 0, x, height, tags='grid')
        
        # Draw horizontal lines
        for i in range(self.region.size[1] + 1):
            y = i * self.cell_size
            self.create_line(0, y, width, y, tags='grid')
    
    def draw_deposits(self):
        """Draw resource deposits"""
        self.delete('deposit')
        self.deposit_markers.clear()
        
        for deposit in self.region.deposits:
            if not deposit.discovered:
                continue
                
            # Random position within the region
            x = self.cell_size * (0.5 + self.region.deposits.index(deposit) % self.region.size[0])
            y = self.cell_size * (0.5 + self.region.deposits.index(deposit) // self.region.size[0])
            
            # Draw deposit marker
            color = 'brown' if deposit.resource_type == 'metal' else 'blue'
            marker = self.create_oval(
                x - 10, y - 10, x + 10, y + 10,
                fill=color, tags='deposit'
            )
            
            # Store reference to marker
            self.deposit_markers[marker] = deposit
            
            # Add tooltip
            self.tag_bind(marker, '<Enter>', 
                         lambda e, d=deposit: self.show_deposit_tooltip(e, d))
            self.tag_bind(marker, '<Leave>', self.hide_deposit_tooltip)
    
    def show_deposit_tooltip(self, event, deposit):
        """Show tooltip with deposit information"""
        tooltip_text = f"{deposit.resource_type.title()}\n"
        tooltip_text += f"Quality: {deposit.quality:.2f}x\n"
        tooltip_text += f"Base Amount: {deposit.base_amount}/h"
        
        # Check if deposit has an active grant
        active_grant = next(
            (g for g in self.region.active_grants if g.deposit == deposit),
            None
        )
        if active_grant:
            tooltip_text += f"\nGrant: {active_grant.time_remaining}"
        
        x, y = event.x, event.y
        self.tooltip = tk.Label(
            self,
            text=tooltip_text,
            bg='white',
            relief='solid',
            borderwidth=1
        )
        self.tooltip.place(x=x + 15, y=y + 15)
    
    def hide_deposit_tooltip(self, event):
        """Hide the deposit tooltip"""
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
            del self.tooltip

class UniverseView(ttk.Frame):
    def __init__(self, parent, game_state):
        super().__init__(parent)
        self.game_state = game_state
        
        # Initialize state variables
        self.drag_start = None
        self.view_offset = [0, 0]
        self.zoom = 1.0
        self.selected_region = None
        
        # Create widgets
        self.create_widgets()
        
        # Start update loop
        self.update_displays()
    
    def create_widgets(self):
        """Create the universe view widgets"""
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create map canvas first
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.grid(row=0, column=1, sticky='nsew')
        
        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=800, height=600,
            background='black'
        )
        self.canvas.pack(fill='both', expand=True)
        
        # Bind mouse events to canvas
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.canvas.bind('<MouseWheel>', self.on_mousewheel)
        
        # Info panel (left side)
        self.info_panel = ttk.Frame(self, padding="5")
        self.info_panel.grid(row=0, column=0, sticky='nsew')
        
        # Region info
        self.region_frame = ttk.LabelFrame(self.info_panel, text="Selected Region", padding="5")
        self.region_frame.pack(fill='x', pady=5)
        
        self.region_name = ttk.Label(self.region_frame, text="No region selected")
        self.region_name.pack(anchor='w')
        
        self.region_coords = ttk.Label(self.region_frame, text="")
        self.region_coords.pack(anchor='w')
        
        self.region_resources = ttk.Label(self.region_frame, text="")
        self.region_resources.pack(anchor='w')
        
        # Travel info
        self.travel_frame = ttk.LabelFrame(self.info_panel, text="Travel", padding="5")
        self.travel_frame.pack(fill='x', pady=5)
        
        self.travel_time = ttk.Label(self.travel_frame, text="")
        self.travel_time.pack(anchor='w')
        
        self.travel_fuel = ttk.Label(self.travel_frame, text="")
        self.travel_fuel.pack(anchor='w')
        
        self.travel_button = ttk.Button(
            self.travel_frame, text="Travel to Region",
            command=self.travel_to_region
        )
        self.travel_button.pack(pady=5)
        self.travel_button['state'] = 'disabled'
    
    def draw_map(self):
        """Draw the universe map"""
        self.canvas.delete('all')  # Clear canvas
        
        # Calculate view bounds
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        center_x = width / 2 - self.view_offset[0]
        center_y = height / 2 - self.view_offset[1]
        
        # Draw grid
        grid_size = 50 * self.zoom
        grid_color = '#1a1a1a'
        
        # Vertical lines
        for x in range(int(-width/grid_size), int(width/grid_size) + 1):
            x_pos = center_x + x * grid_size
            self.canvas.create_line(
                x_pos, 0, x_pos, height,
                fill=grid_color, tags='grid'
            )
        
        # Horizontal lines
        for y in range(int(-height/grid_size), int(height/grid_size) + 1):
            y_pos = center_y + y * grid_size
            self.canvas.create_line(
                0, y_pos, width, y_pos,
                fill=grid_color, tags='grid'
            )
        
        # Draw regions
        for region_name, region in self.game_state.universe.regions.items():
            # Calculate screen position
            x = center_x + (len(region_name) % 5) * grid_size  # Simple layout algorithm
            y = center_y + (len(region_name) // 5) * grid_size
            
            # Draw region circle
            radius = 10 * self.zoom
            color = '#00ff00' if region == self.game_state.current_region else '#ffffff'
            if region == self.selected_region:
                color = '#ffff00'
            
            self.canvas.create_oval(
                x - radius, y - radius,
                x + radius, y + radius,
                fill=color, outline=color,
                tags=('region', region_name)
            )
            
            # Draw region name
            self.canvas.create_text(
                x, y + radius + 5,
                text=region.name,
                fill=color,
                font=('TkDefaultFont', int(8 * self.zoom)),
                tags=('region_name', region_name)
            )
    
    def update_displays(self):
        """Update all displays"""
        self.draw_map()
        self.update_region_info()
        
        # Schedule next update
        self.after(100, self.update_displays)
    
    def update_region_info(self):
        """Update the region info display"""
        if not self.selected_region:
            self.region_name.config(text="No region selected")
            self.region_coords.config(text="")
            self.region_resources.config(text="")
            return
            
        # Update name
        self.region_name.config(text=self.selected_region.name)
        
        # Update coordinates
        self.region_coords.config(
            text=f"Coordinates: ({self.selected_region.x}, {self.selected_region.y})"
        )
        
        # Update resources
        resources_text = "Resources:\n"
        for deposit in self.selected_region.deposits:
            if deposit.discovered:
                resources_text += (
                    f"- {deposit.resource_type.title()}: "
                    f"Quality {deposit.quality:.1f}\n"
                )
        self.region_resources.config(text=resources_text)
    
    def on_click(self, event):
        """Handle mouse click events"""
        self.drag_start = [event.x, event.y]
        
        # Check for region selection
        items = self.canvas.find_closest(event.x, event.y)
        if items:
            tags = self.canvas.gettags(items[0])
            if 'region' in tags:
                region_name = tags[1]
                self.selected_region = self.game_state.universe.regions[region_name]
                self.update_region_info()
    
    def on_drag(self, event):
        """Handle mouse drag events"""
        if self.drag_start:
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            self.view_offset[0] += dx
            self.view_offset[1] += dy
            self.drag_start = [event.x, event.y]
    
    def on_release(self, event):
        """Handle mouse release events"""
        self.drag_start = None
    
    def on_mousewheel(self, event):
        """Handle mouse wheel events for zooming"""
        # Get the direction (-1 for down, 1 for up)
        direction = -1 if event.delta < 0 else 1
        
        # Calculate new zoom level
        zoom_factor = 0.1
        new_zoom = self.zoom * (1 + direction * zoom_factor)
        
        # Clamp zoom level
        self.zoom = max(0.5, min(new_zoom, 2.0))
    
    def travel_to_region(self):
        """Initiate travel to the selected region"""
        if not self.selected_region or self.selected_region == self.game_state.current_region:
            return
        
        # Calculate travel cost
        distance = 1  # For now, all regions are 1 hour apart
        fuel_cost = distance * 10
        
        # Check if we have enough fuel
        if self.game_state.mothership.resources.get('fuel', 0) < fuel_cost:
            messagebox.showerror(
                "Cannot Travel",
                "Not enough fuel for this journey!"
            )
            return
        
        # Start travel
        self.game_state.start_travel(self.selected_region)
        messagebox.showinfo(
            "Travel Started",
            f"Beginning journey to {self.selected_region.name}.\n"
            f"Estimated arrival in {timedelta(hours=distance)}."
        ) 