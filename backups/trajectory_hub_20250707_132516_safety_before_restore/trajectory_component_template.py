"""
Componente de Trayectoria Individual - Sistema de Deltas
======================================================
Gestiona el movimiento de fuentes individuales a lo largo de trayectorias.
"""

import numpy as np
from typing import Dict, Optional
from trajectory_hub.core.delta_system import MotionComponent, MotionDelta
from trajectory_hub.core.motion_components import IndividualTrajectory
import logging

logger = logging.getLogger(__name__)


class TrajectoryComponent(MotionComponent):
    """
    Componente que mueve la fuente a lo largo de una trayectoria individual.
    
    INDEPENDIENTE: No interfiere con otros componentes.
    """
    
    def __init__(self, enabled: bool = True):
        super().__init__(enabled)
        self.trajectory: Optional[IndividualTrajectory] = None
        self.speed: float = 1.0
        self.phase: float = 0.0
        
    def set_trajectory(self, trajectory: IndividualTrajectory):
        """Establece la trayectoria a seguir."""
        self.trajectory = trajectory
        self.phase = 0.0
        
    def calculate_delta(self, state, dt: float, context: Dict = None) -> MotionDelta:
        """
        Calcula el delta para seguir la trayectoria.
        
        NO modifica el estado directamente.
        """
        delta = MotionDelta()
        
        if self.trajectory is None or not self.enabled:
            return delta
            
        # Avanzar en la trayectoria
        self.phase += self.speed * dt
        if self.phase > 1.0:
            self.phase -= 1.0
            
        # Obtener posición objetivo en la trayectoria
        target_pos = self.trajectory.get_position_at_phase(self.phase)
        
        # Calcular delta suave
        direction = target_pos - state.position
        delta.position = direction * 0.1  # Suavizado
        
        return delta
        
    def reset(self):
        """Resetea a la posición inicial."""
        self.phase = 0.0
