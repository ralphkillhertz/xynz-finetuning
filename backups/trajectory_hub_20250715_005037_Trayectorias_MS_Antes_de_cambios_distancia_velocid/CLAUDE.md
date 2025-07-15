# TRAJECTORY HUB - Context for Claude

## Project Overview

**Trajectory Hub** is a real-time 3D spatial trajectory control system for professional audio spatialization. It interfaces with SPAT Revolution (latest version) via OSC protocol to control multiple sound sources in 3D space.

### Dual Focus
1. **Live Performance**: Gesture-based control using LeapMotion and similar devices for intuitive, creative spatialization
2. **Post-Production**: LLM-driven control (via MCP) for synchronized, narrative-driven spatial audio design

### Core Concepts
- **Individual Sources (IS)**: Single sound sources (0-based internally, 1-based in SPAT)
- **Macro Sources (MS)**: Groups of sources representing a single timbre/texture
- **Delta System**: Modular motion system allowing composition of behaviors
- **Formations**: Spatial arrangements (circle, line, grid, spiral, random, sphere)

## Technical Architecture

### Current State (v0.87)
```
main.py → interactive_controller.py → enhanced_trajectory_engine.py → spat_osc_bridge.py → SPAT
```

### Target Architecture
```
UI → SemanticCommand → CommandProcessor → FormationManager → Engine → OSC → SPAT
```

### Key Components

#### Core Engine (`enhanced_trajectory_engine.py`)
- Manages source positions and motion states
- Runs update loop at 60 Hz (target: 120 Hz)
- Accumulates deltas from motion components
- Currently 2273 lines (needs refactoring)

#### Motion System (`motion_components.py`)
- **MotionDelta**: Incremental changes in position/orientation/aperture
- **SourceMotion**: Individual source motion state
- **MacroTrajectory**: Trajectory for macro sources
- Movement modes: fix, forward, backward, pingpong, random
- Displacement modes: absolute, relative, additive

#### OSC Bridge (`spat_osc_bridge.py`)
- Send port: 9000, Receive port: 9001
- Converts 0-based to 1-based indices for SPAT
- Sends positions as `/source/{id}/xyz`
- Handles mute, select, aperture, and other parameters

#### Interactive Controller (`interactive_controller.py`)
- CLI menu system (768 lines, needs refactoring)
- Currently bypasses CommandProcessor (architecture violation)
- Provides access to all system functions

## Performance Requirements
- **Target**: 256 sources at 120 fps
- **Fallback**: 128 sources at 120 fps OR 256 sources at 60 fps
- **Critical**: ALL sources must reach SPAT (current issue: only 16/128 arriving)

## Recent Fixes and Issues

### Fixed
- ✅ Formation bug (all formations appearing as circles) - Fixed by setting `formation_type = None` in `EnhancedMacroSource.__post_init__`
- ✅ Source index offset (macros starting at source 2) - Fixed by setting `_next_source_id = 0`
- ✅ Source 1 separation from group in MS trajectories

### Current Issues
- ⚠️ Only 16 of 128 sources reaching SPAT
- ⚠️ Architecture violations (direct Engine calls)
- ⚠️ File sizes too large (needs modularization)
- ⚠️ CommandProcessor not fully integrated
- ⚠️ Some formations behave strangely (Spiral/Random/Helix)

### In Development
- 🚧 3D Sphere formation
- 🚧 MCP Server for LLM control
- 🚧 Gesture control system
- 🚧 Timeline engine for post-production
- 🚧 SPAT recording control
- 🚧 Perceptual parameters control

## Critical Behaviors

### Formation System
Formations should maintain relative positions while allowing macro movement:
- **Line**: Sources aligned on X-axis
- **Circle**: Sources in circular arrangement
- **Grid**: 2D grid layout
- **Spiral**: Spiral pattern
- **Random**: Random distribution
- **Sphere**: 3D spherical arrangement (pending)

### Delta System Flow
1. Controller creates semantic command
2. Engine interprets and creates motion components
3. Components calculate deltas each frame
4. Engine accumulates deltas
5. Final positions sent via OSC

### Macro Source Behavior
- Sources within a macro maintain formation
- Macro can have trajectory while preserving internal structure
- Individual sources can have additional trajectories
- All motions compose via delta system

## Usage Patterns

### Live Performance Mode
```python
# Create macro with gesture-friendly formation
engine.create_macro("strings", 8, "flock", "circle", 3.0)
# Apply trajectory that responds to gestures
engine.set_macro_trajectory(macro_id, "spiral", speed=2.0)
# Modulate with hand position
engine.set_orientation_modulation(macro_id, orientation_func)
```

### Post-Production Mode
```python
# LLM generates semantic commands
"Move the birds in a flock from left to right over 5 seconds"
# Translates to timed trajectory
engine.create_macro("birds", 12, "flock", "random", 1.5)
engine.set_macro_trajectory_timed("birds", "line", start_pos=[-10,0,0], end_pos=[10,0,0], duration=5.0)
```

## Important Notes

### Coordinate System
- X: Left (-) to Right (+)
- Y: Back (-) to Front (+)
- Z: Down (-) to Up (+)
- Units: Meters in SPAT space

### OSC Messages
- Position: `/source/{id}/xyz x y z`
- Mute: `/source/{id}/mute 0|1`
- Select: `/source/{id}/select 0|1`
- Aperture: `/source/{id}/aperture value`
- Name: `/source/{id}/name "string"`

### Testing Commands
```bash
# Run main interface
python main.py

# Quick test formation
python -c "from trajectory_hub.core.enhanced_trajectory_engine import *; e=EnhancedTrajectoryEngine(); e.start(); e.create_macro('test', 4, 'flock', 'line', 2.0)"
```

## Development Guidelines

1. **Always maintain delta system integrity** - All position changes through deltas
2. **Respect 0-based internal, 1-based SPAT** indexing
3. **Test with multiple sources** to ensure scalability
4. **Preserve gesture-friendly operations** for live mode
5. **Keep LLM integration in mind** for semantic commands

## Common Pitfalls

1. **Formation Default**: MacroSource had default `formation_type = "circle"` causing all formations to be circles
2. **Parameter Order**: `create_macro(name, count, behavior, formation, spacing)` - order matters!
3. **Index Confusion**: Internal uses 0-based, SPAT uses 1-based
4. **Direct Engine Calls**: Should go through CommandProcessor
5. **Update Loop Interference**: Some operations need to happen outside update loop

## Refactorization Strategy (Chief Engineer Plan)

### Current Architecture Problems
1. **Engine (2273 lines)**: Calculates formations internally instead of just applying positions
2. **Interactive Controller (768 lines, 122 methods)**: Should have max 25 methods
3. **Direct Engine calls**: Bypassing CommandProcessor violates architecture
4. **Monolithic files**: Difficult to maintain, test, and optimize

### Migration Roadmap (After Menu Consolidation)

#### Phase 1: Prepare Foundation (1 day)
1. Create comprehensive test suite for current functionality
2. Document all existing behaviors
3. Set up rollback mechanisms
4. Create performance benchmarks

#### Phase 2: Extract Formation Logic (2-3 hours)
1. Modify `Engine.create_macro` to accept `positions[]` instead of formation string
2. Move formation calculations to `FormationManager`
3. Update `CommandProcessor` to orchestrate formation → engine flow
4. Test all formations thoroughly

#### Phase 3: Implement Proper Command Flow (1 day)
1. Create `SemanticCommand` class structure
2. Route all UI calls through `CommandProcessor`
3. Remove direct Engine calls from Interactive Controller
4. Implement command validation and error handling

#### Phase 4: Modularize Interactive Controller (2 days)
1. Extract menu logic into separate modules:
   - `menu_navigation.py` - Menu flow control
   - `menu_display.py` - UI rendering
   - `menu_handlers.py` - Action handlers
2. Reduce to 25 methods maximum
3. Focus solely on user interaction

#### Phase 5: Split Engine into Modules (3 days)
1. Extract components:
   - `source_manager.py` - Source creation/deletion
   - `position_manager.py` - Position updates
   - `delta_accumulator.py` - Delta system
   - `update_loop.py` - Main loop logic
2. Keep Engine as orchestrator only
3. Target: < 500 lines per module

#### Phase 6: Optimize for Performance (2 days)
1. Profile bottlenecks for 256 sources @ 120 fps
2. Implement parallel processing where possible
3. Optimize OSC batching
4. Add performance monitoring

### File Structure Target
```
trajectory_hub/
├── core/
│   ├── engine/
│   │   ├── __init__.py (orchestrator)
│   │   ├── source_manager.py
│   │   ├── position_manager.py
│   │   ├── delta_accumulator.py
│   │   └── update_loop.py
│   ├── motion/
│   │   ├── components.py
│   │   ├── trajectories.py
│   │   └── deformers.py
│   └── formations/
│       ├── manager.py
│       └── calculators.py
├── control/
│   ├── command_processor.py
│   ├── semantic_command.py
│   └── validators.py
└── interface/
    ├── controller.py (< 25 methods)
    ├── menu_navigation.py
    ├── menu_display.py
    └── menu_handlers.py
```

### Testing Strategy
- Unit tests for each module
- Integration tests for command flow
- Performance tests for 256 sources
- Regression tests for all formations

### Rollback Points
- After each phase completion
- Automated backup before major changes
- Git tags for stable versions

## Next Steps (Immediate)

1. **Consolidate Interactive Controller Menu** (current task)
2. **Fix 16/128 source limitation** (critical)
3. **Begin Phase 1 of refactorization**

## Next Steps (Post-Refactorization)

1. Implement MCP server for LLM control
2. Add gesture control support
3. Implement perceptual parameters
4. Add SPAT recording control
5. Create timeline engine for post-production

## Contact and Resources

- SPAT Revolution Documentation: [refer to official docs]
- OSC Protocol: Using python-osc library
- Target Hardware: LeapMotion for gestures
- LLM Integration: Via MCP (Model Context Protocol)

---

*This document serves as context for Claude when working on the Trajectory Hub project. It captures the essential understanding needed to maintain and extend the system while respecting its dual purpose: organic live performance and precise post-production control.*