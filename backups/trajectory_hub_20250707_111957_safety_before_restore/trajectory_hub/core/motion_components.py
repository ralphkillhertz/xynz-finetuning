"""
motion_components.py - Componentes de movimiento actualizados con modulador 3D avanzado
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Callable, Dict, List, Tuple
import numpy as np
from .movement_modes import MovementModeMixin, TrajectoryMovementMode
import time
import logging
from enum import Enum

logger = logging.getLogger(__name__)


@dataclass
class MotionState:
    """Estado completo del movimiento de una fuente"""
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    orientation: np.ndarray = field(default_factory=lambda: np.zeros(3))  # yaw, pitch, roll
    aperture: float = 0.5
    
    # Velocidades para interpolación suave
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    angular_velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    
    # Timestamp para interpolación
    last_update: float = 0.0



# Enums para el sistema de concentración
class ConcentrationMode(Enum):
    """Modos de concentración"""
    FIXED_POINT = "fixed_point"      # Punto fijo en el espacio
    FOLLOW_MACRO = "follow_macro"    # Sigue la trayectoria macro
    DYNAMIC = "dynamic"              # Punto calculado dinámicamente

class ConcentrationCurve(Enum):
    """Curvas de transición"""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    EXPONENTIAL = "exponential"
    BOUNCE = "bounce"

class MotionComponent(ABC):
    """Componente base para todos los tipos de movimiento"""
    
    def __init__(self, name: str = ""):
        self.name = name
        # Offsets para arquitectura de deltas
        self.concentration_offset = np.zeros(3)
        self.macro_rotation_offset = np.zeros(3)
        self.trajectory_offset = np.zeros(3)
        self.algorithmic_rotation_offset = np.zeros(3)
        self.enabled = True
        self.weight = 1.0  # Para mezclar múltiples componentes
        
    @abstractmethod
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        """Actualizar el componente y devolver el estado modificado"""
        pass
        
    def reset(self):
        """Resetear el componente a su estado inicial"""
        pass


class OrientationModulation(MotionComponent):
    """
    Nivel 1: Modulación de orientación básica (yaw, pitch, roll)
    La fuente gira sobre sí misma sin mover su centro
    """
    
    def __init__(self):
        super().__init__("orientation_modulation")
        self.yaw_func: Optional[Callable[[float], float]] = None
        self.pitch_func: Optional[Callable[[float], float]] = None
        self.roll_func: Optional[Callable[[float], float]] = None
        self._orientation_update_threshold = 0.01  # Umbral para actualizar orientación
        self._aperture_update_threshold = 0.01  # Umbral para actualizar apertura
        self.smoothing = 0.1  # Suavizado de cambios
    def set_modulation(self, 
                      yaw: Optional[Callable] = None,
                      pitch: Optional[Callable] = None, 
                      roll: Optional[Callable] = None):
        """Configurar funciones de modulación"""
        if yaw:
            self.yaw_func = yaw
        if pitch:
            self.pitch_func = pitch
        if roll:
            self.roll_func = roll
            
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        if not self.enabled:
            return state
        
        # Código de modulación de orientación aquí
        return state
    def _smooth_angle(self, current: float, target: float, dt: float) -> float:
        """Suavizar transición entre ángulos"""
        # Manejar el wrap-around de ángulos
        diff = target - current
        if diff > np.pi:
            diff -= 2 * np.pi
        elif diff < -np.pi:
            diff += 2 * np.pi
            
        return current + diff * self.smoothing


class AdvancedOrientationModulation(OrientationModulation):
    """
    Modulación avanzada con soporte para P1, P2, P3
    P1: Forma de modulación (combinación de m1, m2, m3)
    P2: Velocidad de modulación (LFO)
    P3: Directividad (Aperture)
    """
    
    def __init__(self, source_id: Optional[int] = None):
        super().__init__()
        self.name = "advanced_orientation_modulation"
        self.source_id = source_id  # ID de la fuente asociada
        self.source_id = source_id  # ID de la fuente asociada
        
        # Parámetros P1 (Forma)
        self.modulation_shape = "circular"  # linear, arc, circular, spiral, lissajous
        self.shape_scale = np.array([1.0, 1.0, 1.0])  # m2(a,b,c) - escala en cada eje
        self.shape_translation = np.array([0.0, 0.0, 0.0])  # m2(d,e) - offset
        self.rotation_mode = "none"  # none, circular, so3
        
        # Parámetros P2 (Velocidad)
        self.lfo_frequency = 0.5  # Hz
        self.lfo_phase = 0.0
        
        # Parámetros P3 (Directividad)
        self.aperture_base = 0.5
        self.aperture_modulation = 0.0
        
        # Control de intensidad global (C2)
        self.intensity = 1.0  # 0.0 a 1.0
        
        # Parámetros internos
        self.time_offset = 0.0
        self.noise_seed = np.random.random()
        
        # Presets predefinidos (alineados con el simulador)
        self.presets = {
            "circle": {
                "shape": "circle",
                "scale": [0.5, 0.5, 0.2],
                "translation": [0.0, 0.0, 0.0],
                "lfo": 1.0,
                "aperture": 0.5,
                "aperture_mod": 0.1,
                "description": "Movimiento circular simple"
            },
            "ellipse": {
                "shape": "ellipse",
                "scale": [0.7, 0.4, 0.1],
                "translation": [0.0, 0.0, 0.0],
                "lfo": 0.8,
                "aperture": 0.6,
                "aperture_mod": 0.1,
                "description": "Movimiento elíptico"
            },
            "lissajous": {
                "shape": "lissajous",
                "scale": [1.0, 0.7, 0.5],
                "translation": [0.0, 0.0, 0.0],
                "lfo": 0.3,
                "aperture": 0.5,
                "aperture_mod": 0.15,
                "description": "Figura de Lissajous 3D"
            },
            "spiral": {
                "shape": "spiral",
                "scale": [1.0, 1.0, 0.5],
                "translation": [0.0, 0.0, 0.0],
                "lfo": 0.1,
                "aperture": 0.9,
                "aperture_mod": 0.05,
                "description": "Espiral expansiva"
            },
            "respiración_suave": {
                "shape": "circle",
                "scale": [0.3, 0.3, 0.1],
                "translation": [0.0, 0.0, 0.0],
                "lfo": 0.2,
                "aperture": 0.7,
                "aperture_mod": 0.1,
                "description": "Movimiento circular suave como respiración"
            },
            "nervioso_aleatorio": {
                "shape": "random",
                "scale": [0.1, 0.1, 0.1],
                "translation": [0.0, 0.0, 0.0],
                "lfo": 5.0,
                "aperture": 0.3,
                "aperture_mod": 0.2,
                "description": "Vibraciones nerviosas aleatorias"
            },
            "espiral_cósmica": {
                "shape": "spiral",
                "scale": [1.0, 1.0, 0.5],
                "translation": [0.0, 0.0, 0.0],
                "lfo": 0.1,
                "aperture": 0.9,
                "aperture_mod": 0.05,
                "description": "Espiral expansiva lenta"
            },
            "lissajous_complejo": {
                "shape": "lissajous",
                "scale": [1.0, 0.7, 0.5],
                "translation": [0.0, 0.0, 0.0],
                "lfo": 0.3,
                "aperture": 0.5,
                "aperture_mod": 0.15,
                "description": "Figura de Lissajous 3D compleja"
            },
            "péndulo_hipnótico": {
                "shape": "pendulum",
                "scale": [0.8, 0.0, 0.6],
                "translation": [0.0, 0.0, 0.0],
                "lfo": 0.4,
                "aperture": 0.6,
                "aperture_mod": 0.1,
                "description": "Movimiento pendular hipnótico"
            },
            "vibración_sísmica": {
                "shape": "seismic",
                "scale": [0.2, 0.2, 0.1],
                "translation": [0.0, 0.0, 0.0],
                "lfo": 8.0,
                "aperture": 0.4,
                "aperture_mod": 0.3,
                "description": "Vibraciones sísmicas rápidas"
            },
            "flotación_oceánica": {
                "shape": "ocean",
                "scale": [0.4, 0.3, 0.5],
                "translation": [0.0, 0.0, 0.0],
                "lfo": 0.15,
                "aperture": 0.8,
                "aperture_mod": 0.1,
                "description": "Movimiento ondulante como en el océano"
            },
            "rotación_mecánica": {
                "shape": "mechanical",
                "scale": [1.0, 0.0, 0.0],
                "translation": [0.0, 0.0, 0.0],
                "lfo": 1.0,
                "aperture": 0.2,
                "aperture_mod": 0.0,
                "description": "Rotación mecánica constante"
            }
        }
        
    def apply_preset(self, preset_name: str):
        """Aplicar un preset predefinido"""
        if preset_name in self.presets:
            preset = self.presets[preset_name]
            self.modulation_shape = preset["shape"]
            self.shape_scale = np.array(preset["scale"])
            self.shape_translation = np.array(preset["translation"])
            self.lfo_frequency = preset["lfo"]
            self.aperture_base = preset["aperture"]
            self.aperture_modulation = preset.get("aperture_mod", 0.0)
            logger.info(f"Preset '{preset_name}' aplicado: {preset['description']}")            
    def interpolate_presets(self, preset1: str, preset2: str, factor: float):
        """Interpolar entre dos presets (0.0 = preset1, 1.0 = preset2)"""
        if preset1 in self.presets and preset2 in self.presets:
            p1 = self.presets[preset1]
            p2 = self.presets[preset2]
            
            # Interpolar parámetros numéricos
            self.shape_scale = np.array(p1["scale"]) * (1-factor) + np.array(p2["scale"]) * factor
            self.shape_translation = np.array(p1["translation"]) * (1-factor) + np.array(p2["translation"]) * factor
            self.lfo_frequency = p1["lfo"] * (1-factor) + p2["lfo"] * factor
            self.aperture_base = p1["aperture"] * (1-factor) + p2["aperture"] * factor
            self.aperture_modulation = p1.get("aperture_mod", 0) * (1-factor) + p2.get("aperture_mod", 0) * factor
            
            # Para la forma, usar el más dominante
            if factor < 0.5:
                self.modulation_shape = p1["shape"]
            else:
                self.modulation_shape = p2["shape"]
                
    def set_intensity(self, intensity: float):
        """Establecer intensidad global de la modulación (0.0 a 1.0)"""
        self.intensity = np.clip(intensity, 0.0, 1.0)
        
    def _perlin_noise(self, x: float, y: float = 0, z: float = 0) -> float:
        """Ruido Perlin simplificado para movimiento orgánico"""
        # Implementación básica de ruido
        def fade(t):
            return t * t * t * (t * (t * 6 - 15) + 10)
        
        def lerp(t, a, b):
            return a + t * (b - a)
        
        # Usar sin() como aproximación para demo
        return np.sin(x * 2.1 + self.noise_seed) * np.cos(y * 1.7) * np.sin(z * 2.3)
        
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        if not self.enabled or self.intensity == 0.0:
            return state
            
        # Calcular fase actual
        phase = (current_time + self.time_offset) * self.lfo_frequency * 2 * np.pi + self.lfo_phase
        
        # Generar modulación según la forma seleccionada
        if self.modulation_shape == "circular" or self.modulation_shape == "circle":
            yaw = np.sin(phase) * self.shape_scale[0]
            pitch = np.cos(phase) * self.shape_scale[1]
            roll = np.sin(phase * 2) * self.shape_scale[2]
            
        elif self.modulation_shape == "ellipse":
            # Elipse: similar al círculo pero con diferentes escalas
            yaw = np.sin(phase) * self.shape_scale[0]
            pitch = np.cos(phase) * self.shape_scale[1] * 0.5  # Elipse más achatada
            roll = np.sin(phase * 2) * self.shape_scale[2]
            
        elif self.modulation_shape == "lissajous":
            yaw = np.sin(phase * 3) * self.shape_scale[0]
            pitch = np.sin(phase * 2) * self.shape_scale[1]
            roll = np.sin(phase * 5) * self.shape_scale[2]
            
        elif self.modulation_shape == "spiral":
            radius = 0.1 + (phase % (2*np.pi)) / (2*np.pi)
            yaw = np.sin(phase) * radius * self.shape_scale[0]
            pitch = np.cos(phase) * radius * self.shape_scale[1]
            roll = phase * 0.1 * self.shape_scale[2]
            
        elif self.modulation_shape == "random":
            # Usar ruido Perlin para movimiento más orgánico
            t = current_time * self.lfo_frequency
            yaw = self._perlin_noise(t, 0, 0) * self.shape_scale[0]
            pitch = self._perlin_noise(0, t, 0) * self.shape_scale[1]
            roll = self._perlin_noise(0, 0, t) * self.shape_scale[2]
            
        elif self.modulation_shape == "pendulum":
            yaw = np.sin(phase) * self.shape_scale[0]
            pitch = 0.0  # Sin movimiento en pitch
            roll = np.sin(phase) * self.shape_scale[2]
            
        elif self.modulation_shape == "seismic":
            # Vibraciones rápidas con envolvente
            envelope = 1.0 - ((phase % (2*np.pi)) / (2*np.pi))
            yaw = np.sin(phase * 20) * envelope * self.shape_scale[0]
            pitch = np.cos(phase * 23) * envelope * self.shape_scale[1]
            roll = np.sin(phase * 17) * envelope * self.shape_scale[2]
            
        elif self.modulation_shape == "ocean":
            # Múltiples ondas superpuestas
            wave1 = np.sin(phase * 0.7) * 0.6
            wave2 = np.sin(phase * 1.3) * 0.3
            wave3 = np.sin(phase * 2.1) * 0.1
            combined = wave1 + wave2 + wave3
            
            yaw = combined * self.shape_scale[0]
            pitch = np.sin(phase * 0.9) * self.shape_scale[1]
            roll = combined * 0.7 * self.shape_scale[2]
            
        elif self.modulation_shape == "mechanical":
            # Rotación constante en yaw
            yaw = (phase % (2*np.pi)) - np.pi  # -π a π
            pitch = 0.0
            roll = 0.0
            
        else:  # linear o default
            yaw = np.sin(phase) * self.shape_scale[0]
            pitch = 0.0
            roll = 0.0
            
        # Aplicar traslación
        yaw += self.shape_translation[0]
        pitch += self.shape_translation[1]
        roll += self.shape_translation[2]
        
        # Aplicar intensidad
        yaw *= self.intensity
        pitch *= self.intensity
        roll *= self.intensity
        
        # Actualizar estado con suavizado
        state.orientation[0] = self._smooth_angle(state.orientation[0], yaw, dt)
        state.orientation[1] = self._smooth_angle(state.orientation[1], pitch, dt)
        state.orientation[2] = self._smooth_angle(state.orientation[2], roll, dt)
        
        # Modular aperture
        aperture_mod = np.sin(phase * 0.5) * self.aperture_modulation * self.intensity
        state.aperture = np.clip(self.aperture_base + aperture_mod, 0.0, 1.0)
        
        return state
        
    def get_state_dict(self) -> Dict:
        """Obtener estado actual para serialización"""
        return {
            "enabled": self.enabled,
            "modulation_shape": self.modulation_shape,
            "shape_scale": self.shape_scale.tolist(),
            "shape_translation": self.shape_translation.tolist(),
            "rotation_mode": self.rotation_mode,
            "lfo_frequency": self.lfo_frequency,
            "lfo_phase": self.lfo_phase,
            "aperture_base": self.aperture_base,
            "aperture_modulation": self.aperture_modulation,
            "intensity": self.intensity,
            "time_offset": self.time_offset
        }
        
    def load_state_dict(self, state: Dict):
        """Cargar estado desde diccionario"""
        self.enabled = state.get("enabled", True)
        self.modulation_shape = state.get("modulation_shape", "circular")
        self.shape_scale = np.array(state.get("shape_scale", [1.0, 1.0, 1.0]))
        self.shape_translation = np.array(state.get("shape_translation", [0.0, 0.0, 0.0]))
        self.rotation_mode = state.get("rotation_mode", "none")
        self.lfo_frequency = state.get("lfo_frequency", 0.5)
        self.lfo_phase = state.get("lfo_phase", 0.0)
        self.aperture_base = state.get("aperture_base", 0.5)
        self.aperture_modulation = state.get("aperture_modulation", 0.0)
        self.intensity = state.get("intensity", 1.0)
        self.time_offset = state.get("time_offset", 0.0)


class IndividualTrajectory(MotionComponent, MovementModeMixin):
    """
    Nivel 2: Trayectoria individual de cada fuente
    Define la forma (círculo, espiral, etc.)
    """
    
    def update_movement(self, dt: float) -> float:
        """Actualizar posición según el modo de movimiento"""
        if self.movement_mode == TrajectoryMovementMode.STOP:
            return self.position_on_trajectory
            
        elif self.movement_mode == TrajectoryMovementMode.FIX:
            # Movimiento normal
            self.position_on_trajectory += self.movement_speed * self.speed_factor * dt
            return self.position_on_trajectory
            
        elif self.movement_mode == TrajectoryMovementMode.RANDOM:
            # Actualizar timer
            self.random_timer += dt
            if self.random_timer >= self.random_interval:
                self.random_timer = 0.0
                self.random_target = np.random.uniform(0, 2 * np.pi)
            
            # Interpolar suavemente hacia el objetivo
            diff = self.random_target - self.position_on_trajectory
            self.position_on_trajectory += diff * (1.0 - self.random_smoothing) * dt
            return self.position_on_trajectory
            
        elif self.movement_mode == TrajectoryMovementMode.VIBRATION:
            # Movimiento base + vibración
            self.position_on_trajectory += self.movement_speed * self.speed_factor * dt
            self.vibration_phase += self.vibration_frequency * dt
            vibration = self.vibration_amplitude * np.sin(self.vibration_phase * 2 * np.pi)
            return self.position_on_trajectory + vibration
            
        elif self.movement_mode == TrajectoryMovementMode.SPIN:
            # Rotación rápida
            self.position_on_trajectory += self.spin_speed * dt
            return self.position_on_trajectory
            
        elif self.movement_mode == TrajectoryMovementMode.FREEZE:
            # Mantener posición congelada
            if self.freeze_position is None:
                self.freeze_position = self.position_on_trajectory
            return self.freeze_position
            
        return self.position_on_trajectory

    def __init__(self, source_id: Optional[int] = None):
        super().__init__("individual_trajectory")
        MovementModeMixin.__init__(self)
        self.trajectory_type = "static"
        self.radius = 1.0
        self.height = 0.0
        self.phase = 0.0
        self.speed = 1.0
        self.center = np.zeros(3)
        self.shape_type = "circle"
        self.movement_mode = TrajectoryMovementMode.FIX
        self.position_on_trajectory = 0.0
        self.movement_speed = 1.0
        self.speed_factor = 1.0  # Factor individual de velocidad (fase)
        self.initial_offset = 0.0  # Offset inicial en la trayectoria
        self.speed_factor = 1.0  # Factor individual de velocidad (fase)
        self.initial_offset = 0.0  # Offset inicial en la trayectoria
        self.vibration_frequency = 2.0
        self.vibration_amplitude = 0.1
        self.vibration_phase = 0.0
        self.random_timer = 0.0
        self.random_target = 0.0
        self.random_interval = 1.0
        self.random_smoothing = 0.8
        self.spin_speed = 10.0
        self.freeze_position = None
        
    def set_trajectory(self, traj_type: str, **params):
        """Configurar tipo y parámetros de trayectoria"""
        self.trajectory_type = traj_type
        self.radius = params.get('radius', 1.0)
        self.height = params.get('height', 0.0)
        self.speed = params.get('speed', 1.0)
        self.center = params.get('center', np.zeros(3))
        
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        """Update trajectory position with rotation support"""
        if not self.enabled:
            return state
        
        # Actualizar posición usando el mixin
        self.position_on_trajectory = self.update_movement(dt)
        
        # Calcular posición basada en la trayectoria
        if hasattr(self, 'trajectory_func') and self.trajectory_func:
            new_position = self.trajectory_func(self.position_on_trajectory)
        else:
            # Trayectoria circular por defecto
            radius = 2.0
            new_position = self.center + np.array([
                radius * np.cos(self.position_on_trajectory),
                radius * np.sin(self.position_on_trajectory),
                0.0
            ])
        
        # APLICAR ROTACIÓN SI EXISTE
        if hasattr(self, 'rotation_matrix') and self.rotation_matrix is not None:
            # Rotar alrededor del centro
            rel_pos = new_position - self.center
            rotated_pos = self.rotation_matrix @ rel_pos
            new_position = self.center + rotated_pos
        
        state.position = new_position
        return state


    def set_rotation(self, pitch: float = 0.0, yaw: float = 0.0, roll: float = 0.0, enabled: bool = True):
        """
        Configurar la rotación de la trayectoria individual
        
        Parameters
        ----------
        pitch : float
            Rotación alrededor del eje X (radianes)
        yaw : float
            Rotación alrededor del eje Y (radianes)
        roll : float
            Rotación alrededor del eje Z (radianes)
        enabled : bool
            Activar/desactivar la rotación
        """
        self.rotation_enabled = enabled
        self.rotation_euler = np.array([pitch, yaw, roll])
        
        # Calcular matriz de rotación
        if enabled:
            # Rotación X (pitch)
            cx, sx = np.cos(pitch), np.sin(pitch)
            rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
            
            # Rotación Y (yaw)
            cy, sy = np.cos(yaw), np.sin(yaw)
            ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
            
            # Rotación Z (roll)
            cz, sz = np.cos(roll), np.sin(roll)
            rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
            
            # Matriz de rotación combinada: R = Rz * Ry * Rx
            self.rotation_matrix = rz @ ry @ rx
        else:
            self.rotation_matrix = np.eye(3)

class MacroMovement(MotionComponent):
    """
    Nivel 3: Movimiento del macro completo
    Afecta al centro de masa del grupo
    """
    
    def __init__(self):
        super().__init__("macro_movement")
        self.trajectory_func: Optional[Callable[[float], np.ndarray]] = None
        self.speed = 1.0
        self.phase = 0.0
        
    def set_trajectory(self, func: Callable[[float], np.ndarray], speed: float = 1.0):
        """Establecer función de trayectoria del macro"""
        self.trajectory_func = func
        self.speed = speed
        
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        if not self.enabled or not self.trajectory_func:
            return state
            
        self.phase += self.speed * dt
        offset = self.trajectory_func(self.phase)
        state.position += offset * self.weight
        
        return state

class MacroTrajectory(MotionComponent, MovementModeMixin):
    """
    Componente para manejar la trayectoria de un macro completo
    Similar a MacroMovement pero con funcionalidad extendida
    """
    
    def __init__(self):
        super().__init__("macro_trajectory")
        MovementModeMixin.__init__(self)
        self.trajectory_func: Optional[Callable[[float], np.ndarray]] = None
        self.orientation_func: Optional[Callable[[float], np.ndarray]] = None
        self.speed = 1.0
        self.phase = 0.0
        self.last_position = np.zeros(3)
        self.last_orientation = np.zeros(3)
        
    def set_trajectory(self, 
                      position_func: Optional[Callable[[float], np.ndarray]] = None,
                      orientation_func: Optional[Callable[[float], np.ndarray]] = None,
                      speed: float = 1.0):
        """Establecer funciones de trayectoria"""
        if position_func is not None:
            self.trajectory_func = position_func
        if orientation_func is not None:
            self.orientation_func = orientation_func
        self.speed = speed
        
    def get_offset(self) -> np.ndarray:
        """Obtener el offset actual del macro"""
        return self.last_position
        
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        if not self.enabled:
            return state
            
        self.phase += self.speed * dt
        
        # Actualizar posición si hay función de trayectoria
        if self.trajectory_func:
            new_position = self.trajectory_func(self.phase)
            if isinstance(new_position, np.ndarray) and new_position.shape == (3,):
                self.last_position = new_position
                state.position = new_position
                
        # Actualizar orientación si hay función
        if self.orientation_func:
            new_orientation = self.orientation_func(self.phase)
            if isinstance(new_orientation, np.ndarray) and new_orientation.shape == (3,):
                self.last_orientation = new_orientation
                state.orientation = new_orientation
                
        return state
        
    def reset(self):
        """Resetear el componente"""
        super().reset()
        self.phase = 0.0
        self.last_position = np.zeros(3)
        self.last_orientation = np.zeros(3)

class GroupBehavior(MotionComponent):
    """
    Nivel 4: Comportamiento de grupo
    Define cómo interactúan las fuentes entre sí
    """
    
    def __init__(self):
        super().__init__("group_behavior")
        self.behavior_type = "independent"
        self.cohesion = 0.5
        self.separation = 0.5
        self.alignment = 0.5
        
    def set_behavior(self, behavior_type: str, **params):
        """Configurar tipo de comportamiento grupal"""
        self.behavior_type = behavior_type
        self.cohesion = params.get('cohesion', 0.5)
        self.separation = params.get('separation', 0.5)
        self.alignment = params.get('alignment', 0.5)
        
    def update(self, time: float, dt: float, state: MotionState, 
               neighbors: List[MotionState] = None) -> MotionState:
        """
        Actualizar considerando estados vecinos
        neighbors: lista de estados de otras fuentes en el grupo
        """
        if not self.enabled or not neighbors:
            return state
            
        if self.behavior_type == "flock":
            # Implementar comportamiento de bandada
            center = np.mean([n.position for n in neighbors], axis=0)
            avg_vel = np.mean([n.velocity for n in neighbors], axis=0)
            
            # Cohesión: moverse hacia el centro del grupo
            cohesion_force = (center - state.position) * self.cohesion
            
            # Separación: evitar colisiones
            separation_force = np.zeros(3)
            for neighbor in neighbors:
                diff = state.position - neighbor.position
                dist = np.linalg.norm(diff)
                if 0 < dist < 2.0:  # Radio de separación
                    separation_force += diff / (dist * dist)
            separation_force *= self.separation
            
            # Alineación: match velocidad promedio
            alignment_force = (avg_vel - state.velocity) * self.alignment
            
            # Aplicar fuerzas
            total_force = cohesion_force + separation_force + alignment_force
            state.velocity += total_force * dt
            state.velocity = np.clip(state.velocity, -5.0, 5.0)  # Limitar velocidad
            
        elif self.behavior_type == "rigid":
            # Mantener formación rígida
            pass
            
        elif self.behavior_type == "elastic":
            # Conexiones elásticas entre fuentes
            pass
            
        elif self.behavior_type == "swarm":
            # Enjambre caótico
            pass
            
        return state


class EnvironmentalForces(MotionComponent):
    """
    Nivel 5: Fuerzas ambientales
    Viento, gravedad, atractores, etc.
    """
    
    def __init__(self):
        super().__init__("environmental_forces")
        self.forces = []
        
    def add_force(self, force_type: str, **params):
        """Añadir una fuerza ambiental"""
        force = {
            'type': force_type,
            'params': params,
            'enabled': True
        }
        self.forces.append(force)
        return len(self.forces) - 1
        
    def remove_force(self, index: int):
        """Eliminar una fuerza"""
        if 0 <= index < len(self.forces):
            self.forces.pop(index)
            
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        if not self.enabled:
            return state
            
        for force in self.forces:
            if not force['enabled']:
                continue
                
            if force['type'] == 'gravity':
                strength = force['params'].get('strength', 9.8)
                direction = force['params'].get('direction', np.array([0, 0, -1]))
                state.velocity += direction * strength * dt
                
            elif force['type'] == 'wind':
                direction = force['params'].get('direction', np.array([1, 0, 0]))
                strength = force['params'].get('strength', 1.0)
                turbulence = force['params'].get('turbulence', 0.1)
                
                wind = direction * strength
                wind += (np.random.random(3) - 0.5) * turbulence
                state.velocity += wind * dt
                
            elif force['type'] == 'attractor':
                position = force['params'].get('position', np.zeros(3))
                strength = force['params'].get('strength', 1.0)
                
                diff = position - state.position
                dist = np.linalg.norm(diff)
                if dist > 0.1:
                    force_vec = diff / dist * strength / (dist + 1)
                    state.velocity += force_vec * dt
                    
            elif force['type'] == 'vortex':
                center = force['params'].get('center', np.zeros(3))
                axis = force['params'].get('axis', np.array([0, 0, 1]))
                strength = force['params'].get('strength', 1.0)
                
                # Vector desde el centro al punto
                to_point = state.position - center
                
                # Componente perpendicular al eje
                perp = to_point - np.dot(to_point, axis) * axis
                perp_norm = np.linalg.norm(perp)
                
                if perp_norm > 0.1:
                    # Dirección tangencial
                    tangent = np.cross(axis, perp / perp_norm)
                    state.velocity += tangent * strength / (perp_norm + 1) * dt
                    
        return state

# ========== CLASES PARA COMPATIBILIDAD CON enhanced_trajectory_engine ==========


# Movido a movement_modes.py
# class TrajectoryMovementMode(Enum):
#     """Modos de movimiento en la trayectoria"""
#     STOP = "stop"
#     FIX = "fix"
#     RANDOM = "random"
#     VIBRATION = "vibration"
#     SPIN = "spin"
#     FREEZE = "freeze"

class TrajectoryDisplacementMode(Enum):
    """Modos de desplazamiento de trayectoria"""
    RELATIVE = "relative"
    ABSOLUTE = "absolute"

class TrajectoryTransform(MotionComponent):
    """Transformación de trayectoria para offset y desplazamiento"""
    
    def __init__(self):
        super().__init__("trajectory_transform")
        self.displacement_mode = TrajectoryDisplacementMode.RELATIVE
        self.offset = np.zeros(3)
        self.macro_reference = np.zeros(3)
        self.macro_velocity = np.zeros(3)
        
    def set_offset(self, offset):
        """Establecer offset (puede ser array o función)"""
        self.offset = offset
        
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        if not self.enabled:
            return state
            
        # Calcular offset actual
        if callable(self.offset):
            current_offset = self.offset(current_time)
        else:
            current_offset = self.offset
            
        if self.displacement_mode == TrajectoryDisplacementMode.ABSOLUTE:
            state.position = current_offset
        else:
            state.position = state.position + current_offset + self.macro_reference
            
        return state

class SourceMotion:
    """
    Contenedor principal para todos los componentes de movimiento de una fuente
    """
    
    def __init__(self, source_id: int):
        self.id = source_id
        self.state = MotionState()
        
        # Componentes de movimiento
        self.components = {
            'orientation_modulation': OrientationModulation(),
            'individual_trajectory': IndividualTrajectory(),
            'trajectory_transform': TrajectoryTransform(),
            'macro_trajectory': MacroMovement(),
            'group_behavior': GroupBehavior(),
            'environmental_forces': EnvironmentalForces(),
            'concentration': ConcentrationComponent(),
        }
        
        # Estado de referencia para macros
        self.macro_reference = np.zeros(3)
        self.macro_velocity = np.zeros(3)
        # Offsets para arquitectura de deltas
        self.concentration_offset = np.zeros(3)
        self.macro_rotation_offset = np.zeros(3)
        self.trajectory_offset = np.zeros(3)
        self.algorithmic_rotation_offset = np.zeros(3)

        
    
    def update(self, dt: float):
        """Actualizar posición aplicando offsets a state.position"""
        if dt < 0.0001:
            return
        
        # Resetear offsets
        self.concentration_offset = np.zeros(3)
        self.macro_rotation_offset = np.zeros(3)
        self.trajectory_offset = np.zeros(3)
        self.algorithmic_rotation_offset = np.zeros(3)
        
        # Posición base del state
        base_pos = self.state.position.copy()
        
        # Calcular offset de concentración
        if 'concentration' in self.components:
            conc = self.components['concentration']
            if hasattr(conc, 'enabled') and conc.enabled and hasattr(conc, 'factor'):
                if conc.factor < 0.99:
                    target = getattr(conc, 'target_point', self.macro_reference)
                    concentrated = base_pos * conc.factor + target * (1 - conc.factor)
                    self.concentration_offset = concentrated - base_pos
        
        # Actualizar la posición sumando offsets
        self.state.position = (base_pos + 
                              self.concentration_offset + 
                              self.macro_rotation_offset +
                              self.trajectory_offset +
                              self.algorithmic_rotation_offset)

    def set_macro_reference(self, position: np.ndarray, velocity: np.ndarray):
        """Establecer referencia del macro para movimiento relativo"""
        self.macro_reference = position
        self.macro_velocity = velocity
        self.components['trajectory_transform'].macro_reference = position
        self.components['trajectory_transform'].macro_velocity = velocity
        
    def reset(self):
        """Resetear todos los componentes"""
        self.state = MotionState()
        for component in self.components.values():
            component.reset()

def create_complex_movement(source_id: int, 
                          trajectory_type: str = "circle",
                          movement_mode: str = "fix",
                          behavior_type: str = "independent") -> SourceMotion:
    """
    Función helper para crear un movimiento complejo con configuración predefinida
    """
    motion = SourceMotion(source_id)
    
    # Configurar trayectoria individual
    motion.components['individual_trajectory'].set_trajectory(trajectory_type)
    
    # Configurar modo de movimiento
    if movement_mode == "fix":
        motion.components['individual_trajectory'].set_movement_mode(
            TrajectoryMovementMode.FIX, movement_speed=1.0
        )
    elif movement_mode == "vibration":
        motion.components['individual_trajectory'].set_movement_mode(
            TrajectoryMovementMode.VIBRATION, 
            vibration_frequency=2.0,
            vibration_amplitude=0.1
        )
    # ... más modos según necesites
    
    # Configurar comportamiento de grupo
    motion.components['group_behavior'].set_behavior(behavior_type)
    
    return motion
        # CONCENTRATION FIX: Position is updated by components
        # No additional sync needed here
    def get_position(self) -> np.ndarray:
        print(f"🔍 DEBUG: SourceMotion.get_position() llamado")
        """Obtener posición final sumando TODOS los componentes"""
        print(f"🔍 DEBUG: Retornando posición: {result}")
        result = (self.macro_reference + 
                self.trajectory_offset + 
                self.concentration_offset + 
                self.macro_rotation_offset +
                self.algorithmic_rotation_offset)
        print(f"🔍 DEBUG: Posición final = {result}")
        return result
    def get_position(self) -> np.ndarray:
        """Obtener posición actual con offsets aplicados"""
        base_pos = self.state.position
        total_offset = np.zeros(3)
        
        # Aplicar todos los offsets
        if hasattr(self, 'concentration_offset'):
            total_offset += self.concentration_offset
        if hasattr(self, 'distribution_offset'):
            total_offset += self.distribution_offset
        if hasattr(self, 'trajectory_offset'):
            total_offset += self.trajectory_offset
            
        return base_pos + total_offset
    
    def get_orientation(self) -> np.ndarray:
        """Obtener orientación actual"""
        return self.state.orientation
    
    def get_aperture(self) -> float:
        """Obtener apertura actual"""
        return self.state.aperture



class ConcentrationComponent(MotionComponent):
    """
    Componente que maneja la concentración/dispersión de fuentes
    Se aplica como último paso después de todos los demás movimientos
    """
    
    def __init__(self):
        super().__init__("concentration")
        
        # Parámetros principales
        self.factor = 1.0  # 0=concentrado, 1=disperso
        self.target_point = np.zeros(3)
        self.mode = ConcentrationMode.FIXED_POINT
        
        # Control de animación
        self.animation_active = False
        self.animation_start_factor = 1.0
        self.animation_target_factor = 0.0
        self.animation_duration = 2.0
        self.animation_elapsed = 0.0
        self.animation_curve = ConcentrationCurve.EASE_IN_OUT
        
        # Parámetros avanzados
        self.include_macro_trajectory = True
        self.attenuate_rotations = True
        self.attenuate_modulations = True
        self.concentration_order = "uniform"
        
        # Cache
        self._macro_center = np.zeros(3)
        self._source_distances = {}
        
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        """Actualizar el componente de concentración"""
        if not self.enabled:
            return state
            
        # Actualizar animación
        if self.animation_active:
            self.animation_elapsed += dt
            progress = min(self.animation_elapsed / self.animation_duration, 1.0)
            
            # Aplicar curva
            curved_progress = self._apply_curve(progress, self.animation_curve)
            
            # Interpolar factor
            self.factor = self.animation_start_factor + \
                         (self.animation_target_factor - self.animation_start_factor) * curved_progress
            
            if progress >= 1.0:
                self.animation_active = False
                
        # No hacer nada si completamente disperso
        if abs(self.factor - 1.0) < 0.001:
            return state
            
        # Calcular punto objetivo
        if self.mode == ConcentrationMode.FOLLOW_MACRO:
            target = self._macro_center + self.target_point
        else:
            target = self.target_point
            
        # Aplicar concentración
        concentration_strength = 1.0 - self.factor
        state.position = self._lerp(state.position, target, concentration_strength)
        
        # Atenuar velocidad
        state.velocity *= self.factor
        
        # Atenuar orientación si está habilitado
        if self.attenuate_rotations:
            state.orientation *= self.factor
            
        return state
        
    def start_animation(self, target_factor: float, duration: float, 
                       curve: ConcentrationCurve = ConcentrationCurve.EASE_IN_OUT):
        """Iniciar animación de concentración"""
        self.animation_start_factor = self.factor
        self.animation_target_factor = max(0.0, min(1.0, target_factor))
        self.animation_duration = max(0.1, duration)
        self.animation_elapsed = 0.0
        self.animation_curve = curve
        self.animation_active = True
        self.enabled = True
        
    def set_factor(self, factor: float):
        """Establecer factor inmediatamente"""
        self.factor = max(0.0, min(1.0, factor))
        self.animation_active = False
        self.enabled = True
        
    def update_macro_center(self, center: np.ndarray):
        """Actualizar centro del macro"""
        self._macro_center = center.copy()
        
    def _lerp(self, a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
        """Interpolación lineal"""
        return a + (b - a) * t
        
    def _apply_curve(self, t: float, curve: ConcentrationCurve) -> float:
        """Aplicar curva de animación"""
        if curve == ConcentrationCurve.LINEAR:
            return t
        elif curve == ConcentrationCurve.EASE_IN:
            return t * t
        elif curve == ConcentrationCurve.EASE_OUT:
            return 1 - (1 - t) * (1 - t)
        elif curve == ConcentrationCurve.EASE_IN_OUT:
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        elif curve == ConcentrationCurve.EXPONENTIAL:
            return t * t * t
        elif curve == ConcentrationCurve.BOUNCE:
            if t < 0.5:
                return 4 * t * t * t
            else:
                p = 2 * t - 2
                return 1 + p * p * p / 2
        return t

