"""
Trajectory Hub v2.0 - Sistema de Trayectorias 3D Inteligentes
"""

from .core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from .core.spat_osc_bridge import SpatOSCBridge, OSCTarget
from .core.motion_components import TrajectoryMovementMode, TrajectoryDisplacementMode
from .core.trajectory_deformers import CompositeDeformer, BlendMode

__version__ = "2.0.0"
__author__ = "Ralph Killhertz (XYNZ)"
__email__ = "ralph@xynz.org"

__all__ = [
    "EnhancedTrajectoryEngine",
    "SpatOSCBridge", 
    "OSCTarget",
    "TrajectoryMovementMode",
    "TrajectoryDisplacementMode", 
    "CompositeDeformer",
    "BlendMode"
]
