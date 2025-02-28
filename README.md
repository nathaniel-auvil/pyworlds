# PyWorlds - Space Fleet Strategy Game

A Python-based space strategy game inspired by classic space strategy games. Command your mothership, manage your fleet, and build a thriving space empire through resource collection, trading, and exploration.

## Features

### Core Systems
- Mothership Management
  - Module System (Collectors, Storage, Production)
  - Power Management and Usage Tracking
  - Crew Assignment and Management
  - Resource Storage and Valuation
  - Module Upgrades with Time-based Progress
- Resource Collection
  - Metal and Gas Collection with Quality Modifiers
  - Energy Generation and Power Distribution
  - Resource Refinement
  - Automatic Storage Management
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

## Testing

The project includes a comprehensive test suite. To run the tests:

```bash
# Run all tests
python -m unittest discover src/pyworld/tests

# Run specific test file
python src/pyworld/tests/test_ship.py

# Run with verbose output
python src/pyworld/tests/test_ship.py -v
```

Key test areas include:
- Module system (power, crew, upgrades)
- Resource collection and storage
- Ship management and resource updates
- Resource value calculations

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
│       │   ├── ship.py    # Ship and module classes
│       │   ├── station.py # Space station functionality
│       │   └── game_state.py
│       ├── tests/         # Test suite
│       │   ├── __init__.py
│       │   └── test_ship.py
│       └── ui/            # User interface components
│           ├── __init__.py
│           ├── main_window.py
│           ├── module_info.py
│           └── station_view.py
```

## Development Status

The game is currently transitioning from a planetary-based economy to a fleet-based system centered around a mothership. Core systems for ship management, resource collection, and space station interaction are being implemented. Recent updates include:
- Enhanced module system with upgrade tracking
- Improved resource collection with storage limits
- Power usage monitoring and management
- Resource value calculations
- Comprehensive test coverage

Check our [ROADMAP.md](ROADMAP.md) for detailed development status and upcoming features.

## Contributing

Contributions are welcome! Please feel free to:
1. Check the [ROADMAP.md](ROADMAP.md) for planned features
2. Create a new branch for your feature
3. Add tests for new functionality
4. Submit a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 