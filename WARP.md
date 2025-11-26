# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a simple Python project that creates an interactive spaceship animation using Pygame. The program displays a controllable spaceship navigating through a starfield background with particle effects for thrust visualization.

## Commands

### Installation
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python3 main.py
```

### Testing
There are no formal tests in this project. To test the application:
1. Run the program with `python3 main.py`
2. Verify the spaceship appears and can be controlled with keyboard inputs
3. Test all controls:
   - Left Arrow / A: Rotate left
   - Right Arrow / D: Rotate right
   - Up Arrow / W: Thrust forward
   - Escape: Quit application

## Architecture

### Core Components

1. **main.py**: Single-file application containing all game logic
   - Game loop implementation
   - Spaceship physics and controls
   - Particle system for thrust effects
   - Star field background generation

### Key Design Patterns

1. **Procedural Generation**: Stars are randomly generated at startup
2. **Particle System**: Thrust effects implemented with simple particle lifecycle management
3. **Screen Wrapping**: Spaceship wraps around screen edges for continuous navigation
4. **Event-Driven Input**: Pygame event system used for keyboard controls

### Technical Details

- **Graphics Library**: Pygame 2.5.1+
- **Math Libraries**: Math module for trigonometric calculations, NumPy 1.22.0+
- **Frame Rate**: Fixed at 60 FPS
- **Screen Resolution**: 800x600 pixels
- **Controls**: Arrow keys or WASD for movement, Escape to exit

## Development Notes

- The project uses Python 3.7+; on this system use `python3` instead of `python`
- All code is contained in a single main.py file
- No testing framework is implemented
- The project is in French (comments and README in French)