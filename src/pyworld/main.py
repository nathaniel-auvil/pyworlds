from .models.game_state import GameState
from .ui.main_window import MainWindow

def main():
    """Main entry point for the game"""
    # Initialize game state
    game_state = GameState()
    
    # Create and run main window
    window = MainWindow(game_state)
    window.run()

if __name__ == "__main__":
    main() 