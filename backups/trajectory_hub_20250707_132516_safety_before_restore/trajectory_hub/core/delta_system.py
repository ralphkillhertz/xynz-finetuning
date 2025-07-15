"""
Sistema de Deltas para Composición Paralela de Movimientos
=========================================================
Permite que múltiples componentes contribuyan al movimiento final
sin interferirse entre sí.
"""

import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class MotionDelta:
    """Representa un cambio incremental en el estado de movimiento."""
    position: np.ndarray = None
    orientation: np.ndarray = None  # [yaw, pitch, roll] en radianes
    aperture: float = 0.0
    
    def __post_init__(self):
        if self.position is None:
            self.position = np.zeros(3)
        if self.orientation is None:
            self.orientation = np.zeros(3)
    
    def __add__(self, other: 'MotionDelta') -> 'MotionDelta':
        """Suma dos deltas."""
        return MotionDelta(
            position=self.position + other.position,
            orientation=self.orientation + other.orientation,
            aperture=self.aperture + other.aperture
        )
    
    def scale(self, factor: float) -> 'MotionDelta':
        """Escala el delta por un factor."""
        return MotionDelta(
            position=self.position * factor,
            orientation=self.orientation * factor,
            aperture=self.aperture * factor
        )


class MotionComponent(ABC):
    """Clase base abstracta para todos los componentes de movimiento."""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.priority = 0  # Mayor prioridad se aplica después
        
    @abstractmethod
    def calculate_delta(self, state: 'MotionState', dt: float, context: Dict = None) -> MotionDelta:
        """
        Calcula el cambio que este componente quiere aplicar.
        
        Args:
            state: Estado actual del movimiento
            dt: Delta time
            context: Información adicional (centro de macro, otras fuentes, etc.)
            
        Returns:
            MotionDelta con los cambios deseados
        """
        pass
    
    def reset(self):
        """Resetea el componente a su estado inicial."""
        pass
    
    def set_enabled(self, enabled: bool):
        """Activa o desactiva el componente."""
        self.enabled = enabled


class DeltaComposer:
    """Gestiona la composición de múltiples deltas."""
    
    @staticmethod
    def compose(base_state: 'MotionState', deltas: List[Tuple[str, MotionDelta]], 
                weights: Dict[str, float] = None) -> 'MotionState':
        """
        Compone múltiples deltas en un nuevo estado.
        
        Args:
            base_state: Estado base
            deltas: Lista de tuplas (nombre_componente, delta)
            weights: Pesos opcionales por componente
            
        Returns:
            Nuevo estado con todos los deltas aplicados
        """
        if weights is None:
            weights = {}
            
        # Comenzar con una copia del estado base
        from trajectory_hub.core.motion_components import MotionState
        new_state = MotionState(
            position=base_state.position.copy(),
            velocity=base_state.velocity.copy(),
            orientation=base_state.orientation.copy(),
            aperture=base_state.aperture
        )
        
        # Acumular todos los deltas
        total_delta = MotionDelta()
        
        for component_name, delta in deltas:
            weight = weights.get(component_name, 1.0)
            if weight != 0:
                weighted_delta = delta.scale(weight)
                total_delta = total_delta + weighted_delta
                
                # Log para debugging
                if np.any(weighted_delta.position != 0):
                    logger.debug(f"{component_name}: Δpos={weighted_delta.position}")
        
        # Aplicar el delta total al estado
        new_state.position += total_delta.position
        new_state.orientation += total_delta.orientation
        new_state.aperture = np.clip(
            new_state.aperture + total_delta.aperture, 
            0.0, 1.0
        )
        
        return new_state


# Componentes de ejemplo que migraremos gradualmente
class LegacyAdapter(MotionComponent):
    """Adaptador temporal para componentes legacy."""
    
    def __init__(self, legacy_update_method):
        super().__init__()
        self.legacy_update = legacy_update_method
        self._last_position = None
        
    def calculate_delta(self, state: 'MotionState', dt: float, context: Dict = None) -> MotionDelta:
        # Guardar posición actual
        self._last_position = state.position.copy()
        
        # Llamar al método legacy (modifica el estado directamente)
        # Esto es temporal mientras migramos
        temp_state = type(state)(
            position=state.position.copy(),
            velocity=state.velocity.copy(),
            orientation=state.orientation.copy(),
            aperture=state.aperture
        )
        
        # El método legacy modificará temp_state
        # Por ahora retornamos delta vacío
        return MotionDelta()
