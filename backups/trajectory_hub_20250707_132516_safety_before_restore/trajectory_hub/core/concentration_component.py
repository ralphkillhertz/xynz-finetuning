"""
Componente de Concentración - Sistema de Deltas
============================================
Hace que las fuentes de un macro converjan hacia su centro.
"""

import numpy as np
from typing import Dict, Optional
from trajectory_hub.core.delta_system import MotionComponent, MotionDelta
import logging

logger = logging.getLogger(__name__)


class ConcentrationComponent(MotionComponent):
    """
    Componente que aplica fuerzas de concentración hacia un punto objetivo.
    
    INDEPENDIENTE: No verifica ni depende de otros componentes.
    """
    
    def __init__(self, enabled: bool = True):
        super().__init__(enabled)
        self.target_position: Optional[np.ndarray] = None
        self.concentration_factor: float = 0.0
        self.smoothing: float = 0.1  # Suavizado del movimiento
        
    def set_target(self, target_position: np.ndarray, factor: float):
        """
        Establece el punto objetivo y la intensidad de concentración.
        
        Args:
            target_position: Posición objetivo (centro del macro)
            factor: Intensidad 0.0 (sin efecto) a 1.0 (máxima concentración)
        """
        self.target_position = target_position.copy()
        self.concentration_factor = np.clip(factor, 0.0, 1.0)
        logger.debug(f"Concentración configurada: target={target_position}, factor={factor}")
        
    def calculate_delta(self, state, dt: float, context: Dict = None) -> MotionDelta:
        """
        Calcula el delta de movimiento hacia el centro.
        
        NO modifica el estado, solo calcula el cambio deseado.
        """
        delta = MotionDelta()
        
        # Si no hay objetivo o el factor es 0, no hay movimiento
        if self.target_position is None or self.concentration_factor == 0:
            return delta
            
        # Calcular dirección hacia el objetivo
        current_pos = state.position
        direction = self.target_position - current_pos
        distance = np.linalg.norm(direction)
        
        # Si ya estamos muy cerca, reducir el movimiento
        if distance < 0.01:
            return delta
            
        # Normalizar dirección
        direction = direction / distance
        
        # Calcular velocidad deseada
        # - Factor de concentración controla la intensidad
        # - Smoothing evita movimientos bruscos
        # - La velocidad disminuye al acercarse (distance factor)
        distance_factor = min(1.0, distance / 5.0)  # Desacelera cerca del objetivo
        desired_speed = self.concentration_factor * self.smoothing * distance_factor
        
        # Delta de posición
        delta.position = direction * desired_speed * dt * 50.0  # Factor de escala para velocidad visible
        
        # Log para debugging
        if np.any(delta.position != 0):
            logger.debug(f"ConcentrationDelta: {np.linalg.norm(delta.position):.4f}")
            
        return delta
    
    def reset(self):
        """Resetea el componente."""
        self.target_position = None
        self.concentration_factor = 0.0
