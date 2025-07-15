"""
trajectory_deformers.py - Sistema avanzado de deformación de trayectorias
Implementa Force Field, Wave, Chaotic y Gesture deformation
"""
from __future__ import annotations

import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Tuple, Any
from enum import Enum
import logging
from scipy.interpolate import interp1d
from collections import deque

logger = logging.getLogger(__name__)


class DeformationType(Enum):
    """Tipos de deformación disponibles"""
    FORCE_FIELD = "force_field"
    WAVE = "wave"
    CHAOTIC = "chaotic"
    GESTURE = "gesture"


class BlendMode(Enum):
    """Modos de mezcla para combinar deformaciones"""
    ADDITIVE = "additive"      # Suma directa
    MULTIPLY = "multiply"      # Multiplicación
    MAXIMUM = "maximum"        # Tomar el mayor
    AVERAGE = "average"        # Promedio
    MORPH = "morph"           # Interpolación


@dataclass
class Attractor:
    """Punto atractor/repulsor en el espacio"""
    position: np.ndarray
    strength: float          # + atrae, - repele
    radius: float           # Radio de influencia
    falloff: str = "smooth" # smooth, linear, sharp, inverse_square
    is_dynamic: bool = False
    trajectory: Optional[Callable[[float], np.ndarray]] = None
    
    def get_position(self, time: float) -> np.ndarray:
        """Obtener posición (puede ser dinámica)"""
        if self.is_dynamic and self.trajectory:
            return self.trajectory(time)
        return self.position


class TrajectoryDeformer(ABC):
    """Clase base para todos los deformadores"""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.enabled = True
        self.weight = 1.0
        self.blend_mode = BlendMode.ADDITIVE
        
    @abstractmethod
    def deform(self, point: np.ndarray, time: float, 
              arc_length: Optional[float] = None,
              trajectory_info: Optional[Dict] = None) -> np.ndarray:
        """
        Aplicar deformación a un punto
        
        Parameters
        ----------
        point : np.ndarray
            Punto a deformar
        time : float
            Tiempo actual
        arc_length : float, optional
            Posición en la curva (0 a longitud total)
        trajectory_info : dict, optional
            Información adicional (tangente, normal, etc.)
            
        Returns
        -------
        np.ndarray
            Vector de deformación (no el punto deformado)
        """
        pass
        
    def reset(self):
        """Resetear estado interno"""
        pass


class ForceFieldDeformation(TrajectoryDeformer):
    """Deformación basada en campos de fuerza/atractores"""
    
    def __init__(self):
        super().__init__("force_field")
        self.attractors: List[Attractor] = []
        self.ambient_force: Optional[Callable[[np.ndarray, float], np.ndarray]] = None
        
    def add_attractor(self, 
                     position: np.ndarray,
                     strength: float,
                     radius: float,
                     falloff: str = "smooth",
                     is_dynamic: bool = False,
                     trajectory: Optional[Callable] = None) -> Attractor:
        """Añadir punto atractor/repulsor"""
        attractor = Attractor(
            position=position.copy(),
            strength=strength,
            radius=radius,
            falloff=falloff,
            is_dynamic=is_dynamic,
            trajectory=trajectory
        )
        self.attractors.append(attractor)
        return attractor
        
    def set_ambient_force(self, force_func: Callable[[np.ndarray, float], np.ndarray]):
        """Establecer campo de fuerza ambiental (ej: viento, gravedad)"""
        self.ambient_force = force_func
        
    def deform(self, point: np.ndarray, time: float, **kwargs) -> np.ndarray:
        deformation = np.zeros(3)
        
        # Aplicar fuerzas de atractores
        for attractor in self.attractors:
            attr_pos = attractor.get_position(time)
            distance = np.linalg.norm(point - attr_pos)
            
            if distance < attractor.radius and distance > 0.001:
                # Calcular fuerza según tipo de caída
                if attractor.falloff == "smooth":
                    # Suave (coseno)
                    factor = 0.5 * (1 + np.cos(np.pi * distance / attractor.radius))
                elif attractor.falloff == "linear":
                    # Lineal
                    factor = 1 - (distance / attractor.radius)
                elif attractor.falloff == "sharp":
                    # Aguda (cuadrática)
                    factor = (1 - distance / attractor.radius) ** 2
                elif attractor.falloff == "inverse_square":
                    # Ley del cuadrado inverso (como gravedad)
                    factor = 1 / (1 + (distance / attractor.radius) ** 2)
                else:
                    factor = 1 - (distance / attractor.radius)
                    
                # Dirección de la fuerza
                if attractor.strength > 0:
                    # Atracción hacia el atractor
                    force_dir = (attr_pos - point) / distance
                else:
                    # Repulsión desde el atractor
                    force_dir = (point - attr_pos) / distance
                    
                force_magnitude = abs(attractor.strength) * factor
                deformation += force_dir * force_magnitude
                
        # Aplicar campo ambiental si existe
        if self.ambient_force:
            deformation += self.ambient_force(point, time)
            
        return deformation * self.weight
        
    def create_vortex(self, center: np.ndarray, axis: np.ndarray, 
                     strength: float, radius: float):
        """Crear campo de vórtice"""
        axis_norm = axis / np.linalg.norm(axis)
        
        def vortex_force(point: np.ndarray, time: float) -> np.ndarray:
            to_center = center - point
            distance_to_axis = np.linalg.norm(to_center - np.dot(to_center, axis_norm) * axis_norm)
            
            if distance_to_axis < radius:
                # Vector tangencial
                radial = to_center - np.dot(to_center, axis_norm) * axis_norm
                if np.linalg.norm(radial) > 0:
                    radial /= np.linalg.norm(radial)
                tangent = np.cross(axis_norm, radial)
                
                # Fuerza proporcional a la distancia
                force = tangent * strength * (1 - distance_to_axis / radius)
                return force
                
            return np.zeros(3)
            
        self.ambient_force = vortex_force


class WaveDeformation(TrajectoryDeformer):
    """Deformación usando ondas que viajan por la trayectoria"""
    
    @dataclass
    class Wave:
        frequency: float        # Frecuencia temporal (Hz)
        amplitude: float       # Amplitud de deformación
        wavelength: float      # Longitud de onda espacial
        direction: str         # radial, tangent, normal, arbitrary
        custom_direction: Optional[np.ndarray] = None
        phase: float = 0.0
        speed: float = 1.0     # Velocidad de propagación
        damping: float = 0.0   # Amortiguación con la distancia
        
    def __init__(self):
        super().__init__("wave")
        self.waves: List[WaveDeformation.Wave] = []
        self.interference_mode = "linear"  # linear, multiplicative
        
    def add_wave(self,
                frequency: float,
                amplitude: float, 
                wavelength: float,
                direction: str = "radial",
                custom_direction: Optional[np.ndarray] = None,
                phase: float = 0.0,
                speed: float = 1.0,
                damping: float = 0.0) -> Wave:
        """Añadir onda deformadora"""
        wave = self.Wave(
            frequency=frequency,
            amplitude=amplitude,
            wavelength=wavelength,
            direction=direction,
            custom_direction=custom_direction,
            phase=phase,
            speed=speed,
            damping=damping
        )
        self.waves.append(wave)
        return wave
        
    def add_breathing_wave(self, period: float, amplitude: float):
        """Añadir onda de "respiración" (expansión/contracción radial)"""
        self.add_wave(
            frequency=1.0 / period,
            amplitude=amplitude,
            wavelength=1000.0,  # Muy larga para afectar toda la trayectoria
            direction="radial",
            speed=0  # No se propaga, afecta todo a la vez
        )
        
    def add_traveling_wave(self, speed: float, amplitude: float, wavelength: float):
        """Añadir onda que viaja por la trayectoria"""
        self.add_wave(
            frequency=speed / wavelength,
            amplitude=amplitude,
            wavelength=wavelength,
            direction="tangent",
            speed=speed
        )
        
    def deform(self, point: np.ndarray, time: float, 
              arc_length: Optional[float] = None,
              trajectory_info: Optional[Dict] = None) -> np.ndarray:
        
        deformation = np.zeros(3)
        
        for wave in self.waves:
            # Calcular fase de la onda
            spatial_phase = 0
            if arc_length is not None:
                spatial_phase = 2 * np.pi * arc_length / wave.wavelength
                
            temporal_phase = 2 * np.pi * wave.frequency * time * wave.speed
            total_phase = spatial_phase - temporal_phase + wave.phase
            
            # Magnitud de la onda
            magnitude = wave.amplitude * np.sin(total_phase)
            
            # Aplicar amortiguación si existe
            if wave.damping > 0 and arc_length is not None:
                magnitude *= np.exp(-wave.damping * arc_length)
                
            # Determinar dirección de deformación
            if wave.direction == "radial":
                # Hacia fuera/dentro desde el origen
                if np.linalg.norm(point) > 0.001:
                    direction = point / np.linalg.norm(point)
                else:
                    direction = np.array([1, 0, 0])
                    
            elif wave.direction == "tangent" and trajectory_info and 'tangent' in trajectory_info:
                # A lo largo de la curva
                direction = trajectory_info['tangent']
                
            elif wave.direction == "normal" and trajectory_info and 'normal' in trajectory_info:
                # Perpendicular a la curva
                direction = trajectory_info['normal']
                
            elif wave.direction == "arbitrary" and wave.custom_direction is not None:
                # Dirección personalizada
                direction = wave.custom_direction / np.linalg.norm(wave.custom_direction)
                
            else:
                # Default: radial
                direction = point / (np.linalg.norm(point) + 0.001)
                
            # Aplicar deformación
            wave_deformation = direction * magnitude
            
            # Modo de interferencia
            if self.interference_mode == "linear":
                deformation += wave_deformation
            elif self.interference_mode == "multiplicative":
                deformation *= (1 + wave_deformation)
                
        return deformation * self.weight


class ChaoticDeformation(TrajectoryDeformer):
    """Deformación usando sistemas dinámicos caóticos"""
    
    def __init__(self, system_type: str = "lorenz"):
        super().__init__("chaotic")
        self.system_type = system_type
        self.state = np.random.randn(3) * 0.1
        self.scale = np.array([0.1, 0.1, 0.1])  # Escala por eje
        self.speed = 1.0
        self.smoothing = 0.1
        
        # Historia para suavizado
        self.history = deque(maxlen=10)
        
        # Parámetros de sistemas
        self.params = self._get_default_params(system_type)
        
    def _get_default_params(self, system_type: str) -> Dict:
        """Obtener parámetros por defecto para cada sistema"""
        params = {
            "lorenz": {"sigma": 10, "rho": 28, "beta": 8/3},
            "rossler": {"a": 0.2, "b": 0.2, "c": 5.7},
            "chua": {"alpha": 15.6, "beta": 28, "m0": -1.143, "m1": -0.714},
            "chen": {"a": 35, "b": 3, "c": 28}
        }
        return params.get(system_type, params["lorenz"])
        
    def set_parameters(self, **params):
        """Ajustar parámetros del sistema"""
        self.params.update(params)
        
    def _lorenz_dynamics(self, state: np.ndarray) -> np.ndarray:
        """Sistema de Lorenz"""
        x, y, z = state
        sigma = self.params["sigma"]
        rho = self.params["rho"]
        beta = self.params["beta"]
        
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
        
        return np.array([dx, dy, dz])
        
    def _rossler_dynamics(self, state: np.ndarray) -> np.ndarray:
        """Sistema de Rössler"""
        x, y, z = state
        a = self.params["a"]
        b = self.params["b"]
        c = self.params["c"]
        
        dx = -y - z
        dy = x + a * y
        dz = b + z * (x - c)
        
        return np.array([dx, dy, dz])
        
    def _chen_dynamics(self, state: np.ndarray) -> np.ndarray:
        """Sistema de Chen"""
        x, y, z = state
        a = self.params["a"]
        b = self.params["b"]
        c = self.params["c"]
        
        dx = a * (y - x)
        dy = (c - a) * x - x * z + c * y
        dz = x * y - b * z
        
        return np.array([dx, dy, dz])
        
    def _update_state(self, dt: float):
        """Actualizar estado del sistema caótico"""
        # Seleccionar dinámica
        if self.system_type == "lorenz":
            dynamics = self._lorenz_dynamics
        elif self.system_type == "rossler":
            dynamics = self._rossler_dynamics
        elif self.system_type == "chen":
            dynamics = self._chen_dynamics
        else:
            dynamics = self._lorenz_dynamics
            
        # Integración Runge-Kutta de 4º orden
        dt_scaled = dt * self.speed
        k1 = dynamics(self.state)
        k2 = dynamics(self.state + 0.5 * dt_scaled * k1)
        k3 = dynamics(self.state + 0.5 * dt_scaled * k2)
        k4 = dynamics(self.state + dt_scaled * k3)
        
        self.state += dt_scaled * (k1 + 2*k2 + 2*k3 + k4) / 6
        
        # Limitar para evitar explosiones
        self.state = np.clip(self.state, -50, 50)
        
    def deform(self, point: np.ndarray, time: float, **kwargs) -> np.ndarray:
        # Actualizar sistema
        self._update_state(0.01)  # dt fijo para consistencia
        
        # Aplicar escala
        deformation = self.state * self.scale
        
        # Suavizado temporal
        self.history.append(deformation.copy())
        if len(self.history) > 1:
            # Promedio ponderado de la historia
            weights = np.exp(-np.arange(len(self.history)) * self.smoothing)
            weights = weights[::-1] / np.sum(weights)
            
            smoothed = np.zeros(3)
            for i, hist in enumerate(self.history):
                smoothed += hist * weights[i]
            deformation = smoothed
            
        return deformation * self.weight
        
    def create_strange_attractor(self, center: np.ndarray, radius: float):
        """Configurar para crear un atractor extraño alrededor de un punto"""
        self.scale = np.array([radius, radius, radius]) * 0.1
        # El sistema caótico ya crea el atractor extraño


class GestureDeformation(TrajectoryDeformer):
    """Deformación basada en gestos grabados o generados"""
    
    @dataclass
    class Gesture:
        points: List[np.ndarray]      # Puntos del gesto
        timestamps: List[float]       # Tiempo de cada punto
        duration: float              # Duración total
        loop: bool = True           # Si se repite
        weight: float = 1.0         # Peso del gesto
        smoothing: float = 0.0      # Suavizado
        
    def __init__(self):
        super().__init__("gesture")
        self.gestures: List[GestureDeformation.Gesture] = []
        self.recording = False
        self.current_recording: List[Tuple[np.ndarray, float]] = []
        self.playback_speed = 1.0
        
    def start_recording(self):
        """Comenzar a grabar un gesto"""
        self.recording = True
        self.current_recording = []
        self.recording_start_time = 0
        
    def add_recording_point(self, point: np.ndarray, time: float):
        """Añadir punto durante la grabación"""
        if self.recording:
            if not self.current_recording:
                self.recording_start_time = time
            self.current_recording.append((point.copy(), time - self.recording_start_time))
            
    def stop_recording(self, loop: bool = True, weight: float = 1.0) -> Optional[Gesture]:
        """Terminar grabación y crear gesto"""
        if not self.recording or len(self.current_recording) < 2:
            self.recording = False
            return None
            
        points = [p for p, _ in self.current_recording]
        timestamps = [t for _, t in self.current_recording]
        duration = timestamps[-1]
        
        gesture = self.Gesture(
            points=points,
            timestamps=timestamps,
            duration=duration,
            loop=loop,
            weight=weight
        )
        
        self.gestures.append(gesture)
        self.recording = False
        self.current_recording = []
        
        return gesture
        
    def add_parametric_gesture(self, 
                             func: Callable[[float], np.ndarray],
                             duration: float,
                             samples: int = 100,
                             loop: bool = True,
                             weight: float = 1.0) -> Gesture:
        """Crear gesto desde función paramétrica"""
        points = []
        timestamps = []
        
        for i in range(samples):
            t = i / (samples - 1) * duration
            points.append(func(t))
            timestamps.append(t)
            
        gesture = self.Gesture(
            points=points,
            timestamps=timestamps,
            duration=duration,
            loop=loop,
            weight=weight
        )
        
        self.gestures.append(gesture)
        return gesture
        
    def add_lemniscate_gesture(self, scale: float = 1.0, duration: float = 4.0):
        """Añadir gesto en forma de lemniscata (∞)"""
        def lemniscate(t):
            theta = t / duration * 2 * np.pi
            return np.array([
                scale * np.cos(theta) / (1 + np.sin(theta)**2),
                scale * np.sin(theta) * np.cos(theta) / (1 + np.sin(theta)**2),
                0
            ])
            
        return self.add_parametric_gesture(lemniscate, duration)
        
    def _interpolate_gesture(self, gesture: Gesture, time: float) -> np.ndarray:
        """Interpolar punto del gesto en tiempo dado"""
        # Manejar loop
        if gesture.loop:
            time = time % gesture.duration
        else:
            time = min(time, gesture.duration)
            
        # Encontrar segmento
        for i in range(len(gesture.timestamps) - 1):
            if gesture.timestamps[i] <= time <= gesture.timestamps[i + 1]:
                # Interpolar entre puntos i e i+1
                t1, t2 = gesture.timestamps[i], gesture.timestamps[i + 1]
                if t2 - t1 > 0:
                    factor = (time - t1) / (t2 - t1)
                else:
                    factor = 0
                    
                p1, p2 = gesture.points[i], gesture.points[i + 1]
                
                if gesture.smoothing > 0 and len(gesture.points) > 2:
                    # Interpolación cúbica para suavizado
                    if i > 0 and i < len(gesture.points) - 2:
                        p0 = gesture.points[i - 1]
                        p3 = gesture.points[i + 2]
                        
                        # Catmull-Rom spline
                        t = factor
                        t2 = t * t
                        t3 = t2 * t
                        
                        point = 0.5 * (
                            (2 * p1) +
                            (-p0 + p2) * t +
                            (2*p0 - 5*p1 + 4*p2 - p3) * t2 +
                            (-p0 + 3*p1 - 3*p2 + p3) * t3
                        )
                    else:
                        # Interpolación lineal en los extremos
                        point = p1 + factor * (p2 - p1)
                else:
                    # Interpolación lineal simple
                    point = p1 + factor * (p2 - p1)
                    
                return point
                
        # Si no se encuentra, devolver último punto
        return gesture.points[-1]
        
    def deform(self, point: np.ndarray, time: float, **kwargs) -> np.ndarray:
        deformation = np.zeros(3)
        
        # Aplicar todos los gestos activos
        for gesture in self.gestures:
            gesture_time = time * self.playback_speed
            gesture_deform = self._interpolate_gesture(gesture, gesture_time)
            deformation += gesture_deform * gesture.weight
            
        return deformation * self.weight


class CompositeDeformer:
    """Sistema que combina múltiples deformadores"""
    
    def __init__(self):
        self.deformers: Dict[str, TrajectoryDeformer] = {
            'force_field': ForceFieldDeformation(),
            'wave': WaveDeformation(),
            'chaotic': ChaoticDeformation(),
            'gesture': GestureDeformation()
        }
        self.active_deformers: List[Tuple[str, float]] = []
        self.global_blend_mode = BlendMode.ADDITIVE
        
    def enable_deformer(self, name: str, weight: float = 1.0):
        """Activar un deformador"""
        if name in self.deformers:
            self.active_deformers.append((name, weight))
            logger.info(f"Deformador '{name}' activado con peso {weight}")
            
    def disable_deformer(self, name: str):
        """Desactivar un deformador"""
        self.active_deformers = [(n, w) for n, w in self.active_deformers if n != name]
        
    def get_deformer(self, name: str) -> Optional[TrajectoryDeformer]:
        """Obtener deformador por nombre"""
        return self.deformers.get(name)
        
    def deform_trajectory(self,
                         base_func: Callable[[float], np.ndarray],
                         t: float,
                         arc_length: Optional[float] = None,
                         trajectory_info: Optional[Dict] = None) -> np.ndarray:
        """Aplicar todas las deformaciones activas"""
        base_point = base_func(t)
        
        if not self.active_deformers:
            return base_point
            
        total_deformation = np.zeros(3)
        
        # Calcular información de trayectoria si es necesaria
        if trajectory_info is None and any(d[0] == 'wave' for d in self.active_deformers):
            # Calcular tangente aproximada
            dt = 0.001
            p_prev = base_func(t - dt)
            p_next = base_func(t + dt)
            tangent = (p_next - p_prev) / (2 * dt)
            if np.linalg.norm(tangent) > 0:
                tangent /= np.linalg.norm(tangent)
                
            # Normal aproximada (asumiendo curva en plano XY principalmente)
            normal = np.cross(tangent, np.array([0, 0, 1]))
            if np.linalg.norm(normal) > 0:
                normal /= np.linalg.norm(normal)
                
            trajectory_info = {
                'tangent': tangent,
                'normal': normal
            }
            
        # Aplicar cada deformador
        deformations = []
        for deformer_name, weight in self.active_deformers:
            deformer = self.deformers[deformer_name]
            if deformer.enabled:
                deform = deformer.deform(
                 point=base_point, 
                 time=t, 
                arc_length=arc_length, 
                trajectory_info=trajectory_info
        )
                deformations.append(deform * weight)
                
        # Combinar según modo de mezcla
        if self.global_blend_mode == BlendMode.ADDITIVE:
            total_deformation = np.sum(deformations, axis=0)
        elif self.global_blend_mode == BlendMode.AVERAGE:
            total_deformation = np.mean(deformations, axis=0)
        elif self.global_blend_mode == BlendMode.MAXIMUM:
            # Tomar la deformación de mayor magnitud
            magnitudes = [np.linalg.norm(d) for d in deformations]
            if magnitudes:
                max_idx = np.argmax(magnitudes)
                total_deformation = deformations[max_idx]
                
        return base_point + total_deformation
        
    def create_preset(self, name: str) -> Dict[str, Any]:
        """Crear preset con configuración actual"""
        preset = {
            'name': name,
            'active_deformers': self.active_deformers.copy(),
            'blend_mode': self.global_blend_mode.value,
            'deformer_states': {}
        }
        
        # Guardar estado de cada deformador
        for deformer_name, deformer in self.deformers.items():
            if hasattr(deformer, '__dict__'):
                state = {k: v for k, v in deformer.__dict__.items() 
                        if not k.startswith('_') and not callable(v)}
                preset['deformer_states'][deformer_name] = state
                
        return preset