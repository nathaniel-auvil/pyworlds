# PyWorlds - Space Strategy Game

A Python-based space strategy game inspired by OGame and Astro Empires. Build your space empire by managing resources, constructing buildings, and developing your infrastructure.

## Features

- Resource Management (Metal, Crystal, Energy)
- Multiple Building Types:
  - Metal Mine
  - Crystal Mine
  - Solar Plant
  - Storage Facility
  - Shipyard
  - Research Lab
- Real-time Resource Production
- Building Upgrades with Construction Times
- Configurable Game Speed
- Save/Load Game System

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pyworlds.git
cd pyworlds
```

2. Install the package:
```bash
pip install -e .
```

## Running the Game

You can run the game in two ways:

1. Using the main script:
```bash
python main.py
```

2. Using the Python module:
```bash
python -m src.pyworld
```

## Game Configuration

The game settings can be configured in `src/pyworld/config.yaml`. This includes:
- Initial resources and storage capacity
- Building properties (production rates, costs, build times)
- Game speed options
- UI settings

## Save System

The game includes an automatic save system. Save files are stored in the `saves` directory in JSON format. You can:
- Save the current game state
- Load a previous save
- List all available saves
- Delete old saves

## Project Structure

```
pyworlds/
├── main.py                 # Main entry point
├── setup.py               # Package installation configuration
├── README.md              # Project documentation
├── src/
│   └── pyworld/
│       ├── __init__.py
│       ├── __main__.py
│       ├── config.yaml    # Game configuration
│       ├── models/        # Game logic and data structures
│       │   ├── __init__.py
│       │   ├── buildings.py
│       │   ├── game_state.py
│       │   └── save_manager.py
│       └── ui/            # User interface components
│           ├── __init__.py
│           ├── main_window.py
│           └── building_info.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 