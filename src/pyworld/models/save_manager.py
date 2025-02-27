import json
import os
from datetime import datetime
from pathlib import Path

class SaveManager:
    def __init__(self, save_dir="saves"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)

    def save_game(self, game_state, save_name=None):
        """Save the current game state to a file."""
        if save_name is None:
            save_name = f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        save_data = {
            'resources': {
                k: v for k, v in game_state.resources.items()
                if k != 'last_update'
            },
            'storage': game_state.storage,
            'buildings': {
                name: {
                    'level': building.level,
                    'current_build': {
                        'start_time': building.current_build['start_time'].isoformat(),
                        'end_time': building.current_build['end_time'].isoformat()
                    } if building.current_build else None
                }
                for name, building in game_state.buildings.items()
            },
            'game_speed': game_state.game_speed,
            'timestamp': datetime.now().isoformat()
        }
        
        save_path = self.save_dir / f"{save_name}.json"
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        return save_path

    def load_game(self, save_name):
        """Load a game state from a save file."""
        save_path = self.save_dir / f"{save_name}.json"
        if not save_path.exists():
            raise FileNotFoundError(f"Save file {save_name} not found")
        
        with open(save_path, 'r') as f:
            save_data = json.load(f)
        
        return save_data

    def list_saves(self):
        """List all available save files."""
        return [f.stem for f in self.save_dir.glob("*.json")]

    def delete_save(self, save_name):
        """Delete a save file."""
        save_path = self.save_dir / f"{save_name}.json"
        if save_path.exists():
            os.remove(save_path)
            return True
        return False 