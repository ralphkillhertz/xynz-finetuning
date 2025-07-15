# trajectory_hub/core/__init__.py
"""
Core components del sistema de trayectorias
"""
from .extended_path_engine import ExtendedPathEngine, TrajectorySystem, PathGenerator
from .enhanced_trajectory_engine import EnhancedTrajectoryEngine
from .motion_components import (
    SourceMotion, 
    TrajectoryMovementMode,
    TrajectoryDisplacementMode,
    OrientationModulation,
    IndividualTrajectory,
    TrajectoryTransform,
    MacroTrajectory
)
from .trajectory_deformers import (
    CompositeDeformer,
    ForceFieldDeformation,
    WaveDeformation,
    ChaoticDeformation,
    GestureDeformation,
    DeformationType,
    BlendMode
)
from .spat_osc_bridge import SpatOSCBridge, OSCTarget
from .distance_controller import TrajectoryDistanceAdjuster, DistanceController

__all__ = [
    # Path Engine
    'ExtendedPathEngine',
    'TrajectorySystem',
    'PathGenerator',
    
    # Enhanced Engine
    'EnhancedTrajectoryEngine',
    
    # Motion Components
    'SourceMotion',
    'TrajectoryMovementMode',
    'TrajectoryDisplacementMode',
    'OrientationModulation',
    'IndividualTrajectory',
    'TrajectoryTransform',
    'MacroTrajectory',
    
    # Deformers
    'CompositeDeformer',
    'ForceFieldDeformation',
    'WaveDeformation', 
    'ChaoticDeformation',
    'GestureDeformation',
    'DeformationType',
    'BlendMode',
    
    # OSC
    'SpatOSCBridge',
    'OSCTarget',
    
    # Distance Control
    'TrajectoryDistanceAdjuster',
    'DistanceController'
]