"""
Componente de Rotación Algorítmica - Sistema de Deltas
====================================================
Aplica rotación alrededor del centro del macro.
"""

import numpy as np
from typing import Dict, Optional
from trajectory_hub.core.delta_system import MotionComponent, MotionDelta
import logging

logger = logging.getLogger(__name__)


class RotationComponent(MotionComponent):
    """
    Componente que rota la fuente alrededor de un centro.
    
    INDEPENDIENTE: Calcula su rotación sin afectar otros componentes.
    """
    
    def __init__(self, enabled: bool = True):
        super().__init__(enabled)
        self.angular_velocity = {'yaw': 0.0, 'pitch': 0.0, 'roll': 0.0}
        self.rotation_center: Optional[np.ndarray] = None
        
    def set_rotation(self, angular_velocity: Dict[str, float], center: np.ndarray):
        """Configura la rotación."""
        self.angular_velocity = angular_velocity.copy()
        self.rotation_center = center.copy()
        
    def calculate_delta(self, state, dt: float, context: Dict = None) -> MotionDelta:
        """
        Calcula el delta de rotación.
        
        Solo retorna el cambio, no modifica estado.
        """
        delta = MotionDelta()
        
        if self.rotation_center is None:
            # Usar centro del contexto si está disponible
            if context and 'macro_center' in context:
                self.rotation_center = context['macro_center']
            else:
                return delta
                
        # Vector desde el centro a la posición actual
        to_source = state.position - self.rotation_center
        
        # Aplicar rotación (simplificado para yaw)
        angle = self.angular_velocity['yaw'] * dt * np.pi / 180.0
        
        # Matriz de rotación 2D para yaw (alrededor del eje Z)
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        
        # Rotar en el plano XY
        new_x = to_source[0] * cos_a - to_source[1] * sin_a
        new_y = to_source[0] * sin_a + to_source[1] * cos_a
        
        # Nueva posición
        new_position = self.rotation_center + np.array([new_x, new_y, to_source[2]])
        
        # Delta es la diferencia
        delta.position = new_position - state.position
        
        return delta
