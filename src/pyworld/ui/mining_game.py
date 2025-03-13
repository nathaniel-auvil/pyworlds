import tkinter as tk
from tkinter import ttk
import random
from datetime import datetime, timedelta
import math

class MiningGame(tk.Toplevel):
    """A mini-game for active resource collection"""
    
    def __init__(self, parent, fleet, callback=None):
        super().__init__(parent)
        self.fleet = fleet
        self.callback = callback
        self.title(f"Mining Operation - {fleet.name}")
        self.geometry("800x600")
        self.resizable(False, False)
        
        # Make the window modal
        self.transient(parent)
        self.grab_set()
        
        # Game state
        self.game_active = False
        self.start_time = None
        self.end_time = None
        self.game_duration = 60  # 60 seconds
        self.score = 0
        self.asteroids = []
        self.last_spawn = datetime.now()
        self.spawn_interval = 1.0  # seconds
        
        # Resources that can be collected
        self.resources = {
            'metal': 0,
            'gas': 0,
            'energy': 0
        }
        
        # Create UI
        self.create_ui()
        
    def create_ui(self):
        """Create the game UI"""
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top info bar
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Time remaining
        self.time_label = ttk.Label(info_frame, text="Time: 60s", font=("Arial", 12))
        self.time_label.pack(side=tk.LEFT, padx=10)
        
        # Score
        self.score_label = ttk.Label(info_frame, text="Score: 0", font=("Arial", 12))
        self.score_label.pack(side=tk.LEFT, padx=10)
        
        # Resources collected
        resources_frame = ttk.Frame(info_frame)
        resources_frame.pack(side=tk.RIGHT)
        
        self.resource_labels = {}
        for resource in self.resources:
            label = ttk.Label(resources_frame, text=f"{resource.title()}: 0", font=("Arial", 12))
            label.pack(side=tk.LEFT, padx=10)
            self.resource_labels[resource] = label
        
        # Game canvas
        self.canvas = tk.Canvas(main_frame, width=780, height=480, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Bottom controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_button = ttk.Button(controls_frame, text="Start Mining", command=self.start_game)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(controls_frame, text="Close", command=self.on_close).pack(side=tk.RIGHT, padx=10)
        
        # Instructions
        instructions = "Click on asteroids to mine resources. Different colors represent different resources."
        ttk.Label(main_frame, text=instructions, font=("Arial", 10)).pack(pady=(10, 0))
        
    def start_game(self):
        """Start the mining mini-game"""
        self.game_active = True
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(seconds=self.game_duration)
        self.score = 0
        self.resources = {resource: 0 for resource in self.resources}
        self.asteroids = []
        
        # Update UI
        self.start_button.config(state=tk.DISABLED)
        self.update_ui()
        
        # Start game loop
        self.update_game()
        
    def update_game(self):
        """Main game loop"""
        if not self.game_active:
            return
            
        now = datetime.now()
        
        # Check if game is over
        if now >= self.end_time:
            self.end_game()
            return
            
        # Update time remaining
        remaining = self.end_time - now
        self.time_label.config(text=f"Time: {int(remaining.total_seconds())}s")
        
        # Spawn new asteroids
        if (now - self.last_spawn).total_seconds() >= self.spawn_interval:
            self.spawn_asteroid()
            self.last_spawn = now
            
        # Update asteroid positions
        self.update_asteroids()
        
        # Schedule next update
        self.after(50, self.update_game)
        
    def spawn_asteroid(self):
        """Spawn a new asteroid on the canvas"""
        if len(self.asteroids) >= 10:  # Limit number of asteroids
            return
            
        # Determine asteroid type and color
        asteroid_type = random.choice(['metal', 'gas', 'energy'])
        colors = {
            'metal': "#A0A0A0",  # Gray
            'gas': "#80C0FF",    # Light blue
            'energy': "#FFFF00"  # Yellow
        }
        
        # Random position and size
        size = random.randint(20, 50)
        x = random.randint(size, 780 - size)
        y = random.randint(size, 480 - size)
        
        # Create asteroid on canvas
        asteroid_id = self.canvas.create_oval(
            x - size/2, y - size/2, 
            x + size/2, y + size/2, 
            fill=colors[asteroid_type], 
            outline="white"
        )
        
        # Store asteroid data
        self.asteroids.append({
            'id': asteroid_id,
            'type': asteroid_type,
            'size': size,
            'x': x,
            'y': y,
            'dx': random.uniform(-2, 2),
            'dy': random.uniform(-2, 2),
            'value': int(size / 5)  # Larger asteroids are worth more
        })
        
    def update_asteroids(self):
        """Update positions of all asteroids"""
        for asteroid in self.asteroids:
            # Move asteroid
            asteroid['x'] += asteroid['dx']
            asteroid['y'] += asteroid['dy']
            
            # Bounce off walls
            if asteroid['x'] - asteroid['size']/2 <= 0 or asteroid['x'] + asteroid['size']/2 >= 780:
                asteroid['dx'] *= -1
            if asteroid['y'] - asteroid['size']/2 <= 0 or asteroid['y'] + asteroid['size']/2 >= 480:
                asteroid['dy'] *= -1
                
            # Update position on canvas
            self.canvas.coords(
                asteroid['id'],
                asteroid['x'] - asteroid['size']/2,
                asteroid['y'] - asteroid['size']/2,
                asteroid['x'] + asteroid['size']/2,
                asteroid['y'] + asteroid['size']/2
            )
            
    def on_canvas_click(self, event):
        """Handle clicks on the canvas"""
        if not self.game_active:
            return
            
        # Check if click hit any asteroid
        for i, asteroid in enumerate(self.asteroids):
            # Calculate distance from click to asteroid center
            distance = math.sqrt((event.x - asteroid['x'])**2 + (event.y - asteroid['y'])**2)
            
            # If click is inside asteroid
            if distance <= asteroid['size']/2:
                # Add to score and resources
                self.score += asteroid['value']
                self.resources[asteroid['type']] += asteroid['value']
                
                # Remove asteroid
                self.canvas.delete(asteroid['id'])
                self.asteroids.pop(i)
                
                # Update UI
                self.update_ui()
                
                # Only process one hit per click
                break
                
    def update_ui(self):
        """Update UI elements"""
        self.score_label.config(text=f"Score: {self.score}")
        
        for resource, amount in self.resources.items():
            self.resource_labels[resource].config(text=f"{resource.title()}: {amount}")
            
    def end_game(self):
        """End the mining game and award resources"""
        self.game_active = False
        
        # Clear canvas
        for asteroid in self.asteroids:
            self.canvas.delete(asteroid['id'])
        self.asteroids = []
        
        # Add resources to fleet
        for resource, amount in self.resources.items():
            if resource in self.fleet.resources:
                self.fleet.add_resource(resource, amount)
        
        # Show results
        result_text = f"Mining complete!\nScore: {self.score}\n\nResources collected:"
        for resource, amount in self.resources.items():
            result_text += f"\n{resource.title()}: {amount}"
            
        result_window = tk.Toplevel(self)
        result_window.title("Mining Results")
        result_window.geometry("300x200")
        result_window.transient(self)
        result_window.grab_set()
        
        ttk.Label(result_window, text=result_text, justify=tk.CENTER).pack(pady=20)
        ttk.Button(result_window, text="OK", command=result_window.destroy).pack(pady=10)
        
        # Re-enable start button
        self.start_button.config(state=tk.NORMAL)
        
        # Call callback if provided
        if self.callback:
            self.callback()
            
    def on_close(self):
        """Handle window close"""
        if self.game_active:
            self.end_game()
        self.destroy() 