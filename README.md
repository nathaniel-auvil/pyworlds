# PyWorlds

A space-based resource management and trading game built using only Prompt engineering.

## Features

- **Fleet Management**: Start with a freighter and expand your fleet
  - Mining drones for resource collection
  - Gas collectors for gas harvesting
  - Upgradeable ships with increased capacity and capabilities

- **Resource System**:
  - Metal mining with drones
  - Gas collection with specialized collectors
  - Energy management for powering equipment
  - Resource storage management
  - Resource trading and refinement

- **Universe Exploration**:
  - Travel between different star systems
  - Discover new resource deposits
  - Establish trade routes

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pyworlds.git
cd pyworlds
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Game

From the project root directory:

```bash
python -m src.pyworld.main
```

## Development

### Running Tests

To run the test suite:

```bash
python -m unittest discover src/pyworld/tests
```

### Project Structure

- `src/pyworld/`
  - `models/`: Game logic and data structures
  - `ui/`: User interface components
  - `tests/`: Unit tests
  - `main.py`: Game entry point

### Current Features

- Overview tab with fleet management
- Universe map for navigation
- Space station interface for trading
- Resource collection and management
- Ship upgrades and equipment management

### Planned Features

- Multiple ship types
- Advanced trading system
- Research and development
- Missions and quests
- Multiplayer support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
