"""
Core components for Trajectory Hub
"""

from .motion_components import (
    MotionState,
    MotionDelta,
    MotionComponent,
    SourceMotion,
    ConcentrationComponent,
    OrientationModulation,
    IndividualTrajectory,
    MacroTrajectory,
    TrajectoryMovementMode,
    TrajectoryDisplacementMode
)

from .enhanced_trajectory_engine import EnhancedTrajectoryEngine
from .spat_osc_bridge import SpatOSCBridge

__all__ = [
    'MotionState',
    'MotionDelta', 
    'MotionComponent',
    'SourceMotion',
    'ConcentrationComponent',
    'OrientationModulation',
    'IndividualTrajectory',
    'MacroTrajectory',
    'TrajectoryMovementMode',
    'TrajectoryDisplacementMode',
    'EnhancedTrajectoryEngine',
    'SpatOSCBridge'
]
