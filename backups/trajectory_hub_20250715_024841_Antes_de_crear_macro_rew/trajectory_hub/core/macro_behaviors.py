"""
macro_behaviors.py - Sistema robusto de comportamientos para Macro Sources
"""
from __future__ import annotations

import numpy as np
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MacroBehaviorType(Enum):
    """Tipos de comportamiento para macros"""
    RIGID = "rigid"          # Todas las fuentes mantienen formación rígida
    FLOCK = "flock"          # Comportamiento de bandada (boids)
    ELASTIC = "elastic"      # Formación elástica con cierta libertad
    INDEPENDENT = "independent"  # Cada fuente sigue su propia versión de la trayectoria


@dataclass
class MacroBehavior:
    """Configuración de comportamiento para un macro"""
    type: MacroBehaviorType = MacroBehaviorType.FLOCK
    
    # Parámetros de formación
    formation_strength: float = 1.0  # Qué tan fuerte mantienen la formación
    formation_flexibility: float = 0.3  # Cuánto pueden desviarse
    
    # Parámetros de bandada (para FLOCK)
    alignment_weight: float = 1.0
    cohesion_weight: float = 1.0
    separation_weight: float = 1.5
    neighbor_radius: float = 3.0
    
    # Parámetros de trayectoria
    trajectory_offset_scale: float = 1.0  # Escala de los offsets individuales
    trajectory_phase_shift: float = 0.0   # Desfase temporal entre fuentes
    trajectory_variation: float = 0.0     # Variación aleatoria en la trayectoria
    
    # Parámetros de orientación
    orientation_mode: str = "aligned"  # "aligned", "tangent", "independent"
    orientation_smoothing: float = 0.1


class MacroBehaviorManager:
    """Gestor de comportamientos para macros"""
    
    def __init__(self):
        self.behaviors: Dict[str, MacroBehavior] = {}
        self._setup_default_behaviors()
        
    def _setup_default_behaviors(self):
        """Configurar comportamientos predefinidos"""
        
        # Bandada natural
        self.behaviors["flock"] = MacroBehavior(
            type=MacroBehaviorType.FLOCK,
            formation_strength=0.3,
            formation_flexibility=0.7,
            alignment_weight=1.0,
            cohesion_weight=0.8,
            separation_weight=1.5,
            orientation_mode="tangent"  # Cada fuente mira hacia donde va
        )
        
        # Formación rígida
        self.behaviors["rigid"] = MacroBehavior(
            type=MacroBehaviorType.RIGID,
            formation_strength=1.0,
            formation_flexibility=0.0,
            trajectory_offset_scale=1.0,
            orientation_mode="aligned"  # Todas miran igual
        )
        
        # Formación elástica
        self.behaviors["elastic"] = MacroBehavior(
            type=MacroBehaviorType.ELASTIC,
            formation_strength=0.7,
            formation_flexibility=0.3,
            trajectory_variation=0.1,
            orientation_mode="tangent"
        )
        
        # Movimiento independiente coordinado (swarm)
        self.behaviors["swarm"] = MacroBehavior(
            type=MacroBehaviorType.INDEPENDENT,
            formation_strength=0.0,
            trajectory_phase_shift=0.1,
            trajectory_variation=0.2,
            orientation_mode="independent"  # Cada uno su orientación
        )
        
    def get_behavior(self, name: str) -> MacroBehavior:
        """Obtener comportamiento por nombre"""
        return self.behaviors.get(name, self.behaviors["flock"])
    
    def create_custom_behavior(self, name: str, **params) -> MacroBehavior:
        """Crear comportamiento personalizado"""
        behavior = MacroBehavior(**params)
        self.behaviors[name] = behavior
        return behavior


class TrajectoryModulator:
    """Modulador de trayectorias para fuentes individuales en un macro"""
    
    @staticmethod
    def apply_rigid_formation(
        base_trajectory: Callable,
        source_positions: List[np.ndarray],
        behavior: MacroBehavior
    ) -> List[Callable]:
        """
        Aplicar formación rígida - todas las fuentes mantienen su offset inicial
        """
        trajectories = []
        center = np.mean(source_positions, axis=0)
        
        for pos in source_positions:
            offset = pos - center
            offset *= behavior.trajectory_offset_scale
            
            def trajectory_with_offset(t, offset=offset):
                return base_trajectory(t) + offset
                
            trajectories.append(trajectory_with_offset)
            
        return trajectories
    
    @staticmethod
    def apply_flock_formation(
        base_trajectory: Callable,
        source_positions: List[np.ndarray],
        behavior: MacroBehavior,
        source_ids: List[int]
    ) -> Dict[int, Callable]:
        """
        Aplicar comportamiento de bandada con variaciones naturales
        """
        trajectories = {}
        n_sources = len(source_positions)
        
        # Centro de masa inicial
        center = np.mean(source_positions, axis=0)
        
        for i, (pos, sid) in enumerate(zip(source_positions, source_ids)):
            # Offset inicial desde el centro
            initial_offset = pos - center
            
            # Fase individual para variación
            phase = i * behavior.trajectory_phase_shift
            
            # Variación aleatoria pero determinista
            np.random.seed(sid)
            variation = np.random.randn(3) * behavior.trajectory_variation
            
            def make_trajectory(base_func, offset, phase, var):
                def traj(t):
                    # Trayectoria base con fase
                    base_pos = base_func(t + phase)
                    
                    # Aplicar offset con flexibilidad
                    # El offset "respira" con el tiempo
                    flex_offset = offset * (1 - behavior.formation_flexibility * 0.5 * np.sin(t * 0.5))
                    
                    # Añadir variación suave
                    var_offset = var * np.sin(t * 2 + phase)
                    
                    return base_pos + flex_offset + var_offset
                    
                return traj
                
            trajectories[sid] = make_trajectory(base_trajectory, initial_offset, phase, variation)
            
        return trajectories
    
    @staticmethod
    def apply_elastic_formation(
        base_trajectory: Callable,
        source_positions: List[np.ndarray],
        behavior: MacroBehavior
    ) -> List[Callable]:
        """
        Aplicar formación elástica - como si estuvieran conectadas por resortes
        """
        trajectories = []
        center = np.mean(source_positions, axis=0)
        
        for i, pos in enumerate(source_positions):
            offset = pos - center
            
            def elastic_trajectory(t, offset=offset, idx=i):
                base_pos = base_trajectory(t)
                
                # Offset elástico que varía con el tiempo
                # Simula un resorte que se estira y contrae
                elastic_factor = 1 + behavior.formation_flexibility * np.sin(t * 0.3 + idx * 0.5)
                elastic_offset = offset * elastic_factor * behavior.trajectory_offset_scale
                
                # Añadir pequeña oscilación perpendicular
                perpendicular = np.array([-offset[1], offset[0], 0])
                if np.linalg.norm(perpendicular) > 0:
                    perpendicular /= np.linalg.norm(perpendicular)
                oscillation = perpendicular * 0.1 * np.sin(t * 2 + idx)
                
                return base_pos + elastic_offset + oscillation
                
            trajectories.append(elastic_trajectory)
            
        return trajectories
    
    @staticmethod
    def apply_independent_formation(
        base_trajectory: Callable,
        source_positions: List[np.ndarray],
        behavior: MacroBehavior,
        n_sources: int
    ) -> List[Callable]:
        """
        Aplicar movimiento independiente coordinado - cada fuente con su propia variación
        """
        trajectories = []
        
        for i in range(n_sources):
            # Cada fuente tiene un desfase único
            phase = i * behavior.trajectory_phase_shift * 2 * np.pi / n_sources
            
            # Cada fuente tiene su propia variación de escala
            np.random.seed(i)
            scale_var = 1 + (np.random.rand() - 0.5) * behavior.trajectory_variation
            
            # Variación en velocidad
            speed_var = 1 + (np.random.rand() - 0.5) * 0.3
            
            def independent_trajectory(t, phase=phase, scale=scale_var, speed=speed_var):
                # Aplicar fase y escala individual
                pos = base_trajectory(t * speed + phase)
                
                # Escalar la trayectoria
                pos = pos * scale
                
                # Añadir deriva suave
                drift = np.array([
                    0.5 * np.sin(t * 0.1 + phase),
                    0.5 * np.cos(t * 0.15 + phase),
                    0.3 * np.sin(t * 0.12 + phase)
                ])
                
                return pos + drift
                
            trajectories.append(independent_trajectory)
            
        return trajectories


class OrientationController:
    """Controlador de orientación para fuentes en macros"""
    
    @staticmethod
    def calculate_aligned_orientation(
        positions: np.ndarray,
        velocities: np.ndarray,
        behavior: MacroBehavior
    ) -> np.ndarray:
        """
        Calcular orientación alineada - todas miran en la misma dirección
        """
        # Velocidad promedio del grupo
        avg_velocity = np.mean(velocities, axis=0)
        
        # Calcular yaw desde la velocidad promedio
        yaw = np.arctan2(avg_velocity[1], avg_velocity[0])
        
        # Pitch desde la componente Z
        horizontal_speed = np.sqrt(avg_velocity[0]**2 + avg_velocity[1]**2)
        pitch = np.arctan2(avg_velocity[2], horizontal_speed) if horizontal_speed > 0.01 else 0
        
        # Aplicar a todas las fuentes
        n_sources = len(positions)
        orientations = np.zeros((n_sources, 3))
        orientations[:, 0] = yaw
        orientations[:, 1] = pitch
        # Roll se mantiene en 0 para orientación alineada
        
        return orientations
    
    @staticmethod
    def calculate_tangent_orientation(
        positions: np.ndarray,
        velocities: np.ndarray,
        behavior: MacroBehavior
    ) -> np.ndarray:
        """
        Calcular orientación tangente - cada fuente mira hacia donde va
        """
        orientations = np.zeros((len(positions), 3))
        
        for i, vel in enumerate(velocities):
            # Yaw desde velocidad individual
            orientations[i, 0] = np.arctan2(vel[1], vel[0])
            
            # Pitch desde velocidad individual
            horizontal_speed = np.sqrt(vel[0]**2 + vel[1]**2)
            if horizontal_speed > 0.01:
                orientations[i, 1] = np.arctan2(vel[2], horizontal_speed)
                
        return orientations
    
    @staticmethod
    def calculate_independent_orientation(
        positions: np.ndarray,
        time: float,
        behavior: MacroBehavior
    ) -> np.ndarray:
        """
        Calcular orientación independiente - cada fuente rota por su cuenta
        """
        n_sources = len(positions)
        orientations = np.zeros((n_sources, 3))
        
        for i in range(n_sources):
            # Rotación individual basada en tiempo y posición
            orientations[i, 0] = time * (1 + i * 0.1)  # Yaw - velocidad variable
            orientations[i, 1] = np.sin(time * 0.5 + i * 0.2) * 0.3  # Pitch - oscilación
            orientations[i, 2] = np.sin(time * 0.3 + i * 0.3) * 0.1  # Roll - pequeña rotación
            
        return orientations


# Funciones de utilidad para debugging y visualización
def describe_behavior(behavior_name: str) -> str:
    """Obtener descripción detallada de un comportamiento"""
    descriptions = {
        "flock": """
        FLOCK - Bandada Natural
        Las fuentes se mueven como pájaros o peces:
        - Se mantienen cerca pero con libertad
        - Evitan colisiones entre ellas
        - Siguen la dirección general del grupo
        - Cada una mira hacia donde va
        """,
        
        "rigid": """
        RIGID - Formación Rígida
        Las fuentes mantienen formación perfecta:
        - Distancias fijas entre fuentes
        - Movimiento perfectamente sincronizado
        - Todas miran en la misma dirección
        - Como drones en exhibición
        """,
        
        "elastic": """
        ELASTIC - Formación Elástica
        Las fuentes están conectadas flexiblemente:
        - Como unidas por resortes invisibles
        - La formación se deforma y recupera
        - Movimiento fluido y orgánico
        - Como medusas o gelatina
        """,
        
        "swarm": """
        SWARM - Enjambre Independiente
        Cada fuente es independiente pero coordinada:
        - Cada una sigue su propia versión de la trayectoria
        - Desfases temporales crean patrones
        - Como abejas o partículas
        - Caos organizado
        """
    }
    
    return descriptions.get(behavior_name, "Comportamiento desconocido")