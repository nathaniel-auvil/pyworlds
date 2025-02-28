import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.pyworld.models.game_state import GameState
from src.pyworld.ui.main_window import MainWindow

def main():
    """Main entry point for PyWorlds"""
    # Create game state
    game_state = GameState()
    
    # Create and run main window
    window = MainWindow(game_state)
    window.run()

if __name__ == '__main__':
    main() 