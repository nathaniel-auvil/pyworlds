# PyWorlds - Space Fleet Strategy Game

A Python-based space strategy game inspired by classic space strategy games. Command your mothership, manage your fleet, and build a thriving space empire through resource collection, trading, and exploration.

## Features

### Core Systems
- Mothership Management
  - Module System (Collectors, Storage, Production)
  - Power Management
  - Crew Assignment
  - Resource Storage
- Resource Collection
  - Metal and Gas Collection
  - Energy Generation
  - Resource Refinement
- Space Station Interaction
  - Trading System
  - Mission System
  - Blueprint Research

### Planned Features
See our [ROADMAP.md](ROADMAP.md) for detailed development plans including:
- Fleet Management
- Advanced Trading
- Space Exploration
- Random Events
- And more!

## Installation

1. Clone the repository:
```bash
git clone https://github.com/nathaniel-auvil/pyworlds.git
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
- Module properties (collection rates, power usage, crew requirements)
- Game speed options
- UI settings

## Project Structure

```
pyworlds/
├── main.py                 # Main entry point
├── setup.py               # Package installation configuration
├── README.md              # Project documentation
├── ROADMAP.md            # Development roadmap
├── src/
│   └── pyworld/
│       ├── __init__.py
│       ├── __main__.py
│       ├── config.yaml    # Game configuration
│       ├── assets/        # Game assets (icons, etc.)
│       ├── models/        # Game logic and data structures
│       │   ├── __init__.py
│       │   ├── ship.py
│       │   ├── station.py
│       │   └── game_state.py
│       └── ui/            # User interface components
│           ├── __init__.py
│           ├── main_window.py
│           ├── module_info.py
│           └── station_view.py
```

## Development Status

The game is currently transitioning from a planetary-based economy to a fleet-based system centered around a mothership. Core systems for ship management, resource collection, and space station interaction are being implemented. Check our [ROADMAP.md](ROADMAP.md) for detailed development status and upcoming features.

## Contributing

Contributions are welcome! Please feel free to:
1. Check the [ROADMAP.md](ROADMAP.md) for planned features
2. Create a new branch for your feature
3. Submit a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 