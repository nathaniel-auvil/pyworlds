import os
import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path

class IconManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IconManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.icons = {}
        self.icon_size = (16, 16)  # Default icon size
        
        # Get the assets directory path
        self.assets_dir = Path(__file__).parent.parent / 'assets' / 'icons'
        
        # Define icon paths relative to assets/icons directory
        self.icon_paths = {
            # Resources
            'metal': 'metal.png',
            'crystal': 'crystal.png',
            'energy': 'energy.png',
            
            # Buildings
            'metal_mine': 'metal_mine.png',
            'crystal_mine': 'crystal_mine.png',
            'solar_plant': 'solar_plant.png',
            'storage_facility': 'storage.png',
            'shipyard': 'shipyard.png',
            'research_lab': 'research.png',
            
            # UI elements
            'info': 'info.png',
            'upgrade': 'upgrade.png',
        }
    
    def load_icon(self, icon_name):
        """Load an icon and cache it."""
        if icon_name in self.icons:
            return self.icons[icon_name]
            
        icon_path = self.assets_dir / self.icon_paths[icon_name]
        if not icon_path.exists():
            print(f"Warning: Icon {icon_name} not found at {icon_path}")
            return None
            
        try:
            image = Image.open(icon_path)
            image = image.resize(self.icon_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.icons[icon_name] = photo
            return photo
        except Exception as e:
            print(f"Error loading icon {icon_name}: {e}")
            return None
    
    def get_icon(self, icon_name):
        """Get an icon, loading it if necessary."""
        return self.load_icon(icon_name)
    
    def set_icon_size(self, width, height):
        """Set the size for newly loaded icons."""
        self.icon_size = (width, height)
        # Clear cache to force reload at new size
        self.icons.clear() 