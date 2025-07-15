"""
trajectory_functions.py - Funciones de trayectoria 3D mejoradas para macros
Soporta trayectorias cerradas y abiertas con velocidades bidireccionales
"""
import numpy as np
from typing import Callable, Dict, Any, Tuple, Optional
import math


def create_trajectory_function(trajectory_type: str, **kwargs) -> Callable[[float], np.ndarray]:
    """
    Crea una función de trayectoria a partir de un tipo string
    
    Args:
        trajectory_type: Tipo de trayectoria (circle, spiral, etc.)
        **kwargs: Parámetros específicos de la trayectoria
        
    Returns:
        Función que recibe t y retorna posición [x, y, z]
    """
    # Convertir a callable numpy
    if trajectory_type == "circle":
        return _create_circle_trajectory(**kwargs)
    elif trajectory_type == "spiral":
        return _create_spiral_trajectory(**kwargs)
    elif trajectory_type == "figure8":
        return _create_figure8_trajectory(**kwargs)
    elif trajectory_type == "lissajous":
        return _create_lissajous_trajectory(**kwargs)
    elif trajectory_type == "random":
        return _create_random_trajectory(**kwargs)
    elif trajectory_type == "helix":
        return _create_helix_trajectory(**kwargs)
    elif trajectory_type == "line":
        return _create_line_trajectory(**kwargs)
    elif trajectory_type == "wave":
        return _create_wave_trajectory(**kwargs)
    elif trajectory_type == "torus_knot":
        return _create_torus_knot_trajectory(**kwargs)
    else:
        # Intentar con las funciones legacy
        if trajectory_type in LEGACY_FUNCTIONS:
            return _create_legacy_wrapper(trajectory_type, **kwargs)
        raise ValueError(f"Tipo de trayectoria '{trajectory_type}' no reconocido")


def _create_circle_trajectory(**kwargs) -> Callable[[float], np.ndarray]:
    """Círculo 3D en plano configurable"""
    radius = kwargs.get("radius", 5.0)
    plane = kwargs.get("plane", "xy")  # xy, xz, yz
    center = kwargs.get("center", np.zeros(3))
    
    def trajectory(t: float) -> np.ndarray:
        # t ya viene normalizado [0,1] desde el componente
        angle = t * 2 * np.pi
        
        if plane == "xy":
            x = center[0] + radius * np.cos(angle)
            y = center[1] + radius * np.sin(angle)
            z = center[2]
        elif plane == "xz":
            x = center[0] + radius * np.cos(angle)
            y = center[1]
            z = center[2] + radius * np.sin(angle)
        else:  # yz
            x = center[0]
            y = center[1] + radius * np.cos(angle)
            z = center[2] + radius * np.sin(angle)
            
        return np.array([x, y, z])
    
    trajectory.is_closed = True
    trajectory.trajectory_type = "circle"
    return trajectory


def _create_spiral_trajectory(**kwargs) -> Callable[[float], np.ndarray]:
    """Espiral 3D (helicoidal)"""
    radius = kwargs.get("radius", 5.0)
    height = kwargs.get("height", 10.0)
    turns = kwargs.get("turns", 3.0)
    center = kwargs.get("center", np.zeros(3))
    
    def trajectory(t: float) -> np.ndarray:
        
        angle = t * turns * 2 * np.pi
        current_radius = radius * (0.2 + 0.8 * t)
        
        x = center[0] + current_radius * np.cos(angle)
        y = center[1] + current_radius * np.sin(angle)
        z = center[2] + t * height
        
        return np.array([x, y, z])
    
    trajectory.is_closed = False
    trajectory.trajectory_type = "spiral"
    return trajectory


def _create_figure8_trajectory(**kwargs) -> Callable[[float], np.ndarray]:
    """Figura de 8 (Lissajous 3D)"""
    scale = kwargs.get("scale", 5.0)
    center = kwargs.get("center", np.zeros(3))
    
    def trajectory(t: float) -> np.ndarray:
        
        angle = t * 2 * np.pi
        x = center[0] + scale * np.sin(2 * angle)
        y = center[1] + scale * np.sin(angle)
        z = center[2]
        
        return np.array([x, y, z])
    
    trajectory.is_closed = True
    trajectory.trajectory_type = "figure8"
    return trajectory


def _create_lissajous_trajectory(**kwargs) -> Callable[[float], np.ndarray]:
    """Curva de Lissajous 3D general"""
    scale = kwargs.get("scale", 5.0)
    freq_x = kwargs.get("freq_x", 3.0)
    freq_y = kwargs.get("freq_y", 2.0)
    freq_z = kwargs.get("freq_z", 4.0)
    center = kwargs.get("center", np.zeros(3))
    
    def trajectory(t: float) -> np.ndarray:
        
        angle = t * 2 * np.pi
        x = center[0] + scale * np.sin(freq_x * angle)
        y = center[1] + scale * np.sin(freq_y * angle)
        z = center[2] + scale * 0.5 * np.sin(freq_z * angle)
        
        return np.array([x, y, z])
    
    trajectory.is_closed = True
    trajectory.trajectory_type = "lissajous"
    return trajectory


def _create_random_trajectory(**kwargs) -> Callable[[float], np.ndarray]:
    """Movimiento aleatorio suavizado"""
    scale = kwargs.get("scale", 5.0)
    seed = kwargs.get("seed", 42)
    num_points = kwargs.get("num_points", 10)
    center = kwargs.get("center", np.zeros(3))
    
    # Generar puntos de control
    np.random.seed(seed)
    control_points = np.random.randn(num_points, 3) * scale
    control_points[-1] = control_points[0] + np.random.randn(3) * 0.5
    
    def trajectory(t: float) -> np.ndarray:
        
        scaled_t = t * (num_points - 1)
        idx = int(scaled_t)
        frac = scaled_t - idx
        
        if idx >= num_points - 1:
            return center + control_points[-1]
        
        # Interpolación suave
        smooth_frac = 0.5 * (1 - np.cos(frac * np.pi))
        p1 = control_points[idx]
        p2 = control_points[idx + 1]
        
        position = p1 + (p2 - p1) * smooth_frac
        return center + position
    
    trajectory.is_closed = False
    trajectory.trajectory_type = "random"
    return trajectory


def _create_helix_trajectory(**kwargs) -> Callable[[float], np.ndarray]:
    """Hélice 3D"""
    radius = kwargs.get("radius", 5.0)
    pitch = kwargs.get("pitch", 2.0)
    turns = kwargs.get("turns", 3.0)
    center = kwargs.get("center", np.zeros(3))
    
    def trajectory(t: float) -> np.ndarray:
        
        angle = t * turns * 2 * np.pi
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
        z = center[2] + t * turns * pitch
        
        return np.array([x, y, z])
    
    trajectory.is_closed = False
    trajectory.trajectory_type = "helix"
    return trajectory


def _create_line_trajectory(**kwargs) -> Callable[[float], np.ndarray]:
    """Línea recta 3D"""
    start = kwargs.get("start", np.array([0.0, 0.0, 0.0]))
    end = kwargs.get("end", np.array([10.0, 0.0, 0.0]))
    
    def trajectory(t: float) -> np.ndarray:
        
        position = start + t * (end - start)
        return position
    
    trajectory.is_closed = False
    trajectory.trajectory_type = "line"
    return trajectory


def _create_wave_trajectory(**kwargs) -> Callable[[float], np.ndarray]:
    """Onda sinusoidal 3D"""
    length = kwargs.get("length", 20.0)
    amplitude = kwargs.get("amplitude", 3.0)
    frequency = kwargs.get("frequency", 2.0)
    axis = kwargs.get("axis", "x")
    wave_axis = kwargs.get("wave_axis", "y")
    center = kwargs.get("center", np.zeros(3))
    
    axis_map = {"x": 0, "y": 1, "z": 2}
    
    def trajectory(t: float) -> np.ndarray:
        
        main_pos = t * length
        wave_pos = amplitude * np.sin(t * frequency * 2 * np.pi)
        
        position = center.copy()
        position[axis_map[axis]] += main_pos
        position[axis_map[wave_axis]] += wave_pos
        
        return position
    
    trajectory.is_closed = False
    trajectory.trajectory_type = "wave"
    return trajectory


def _create_torus_knot_trajectory(**kwargs) -> Callable[[float], np.ndarray]:
    """Nudo toroidal"""
    R = kwargs.get("major_radius", 5.0)
    r = kwargs.get("minor_radius", 2.0)
    p = kwargs.get("p", 2)
    q = kwargs.get("q", 3)
    center = kwargs.get("center", np.zeros(3))
    
    def trajectory(t: float) -> np.ndarray:
        
        angle = t * 2 * np.pi
        x = center[0] + (R + r * np.cos(q * angle)) * np.cos(p * angle)
        y = center[1] + (R + r * np.cos(q * angle)) * np.sin(p * angle)
        z = center[2] + r * np.sin(q * angle)
        
        return np.array([x, y, z])
    
    trajectory.is_closed = True
    trajectory.trajectory_type = "torus_knot"
    return trajectory


def _create_legacy_wrapper(trajectory_type: str, **kwargs) -> Callable[[float], np.ndarray]:
    """Wrapper para funciones legacy que retornan tuplas"""
    legacy_func = LEGACY_FUNCTIONS[trajectory_type]
    scale = kwargs.get("scale", 5.0)
    center = kwargs.get("center", np.zeros(3))
    
    def trajectory(t: float) -> np.ndarray:
        
        x, y, z = legacy_func(t)
        return center + np.array([x * scale, y * scale, z * scale])
    
    # Las funciones legacy son generalmente cerradas excepto spiral
    trajectory.is_closed = trajectory_type != "spiral"
    trajectory.trajectory_type = trajectory_type
    return trajectory


# Funciones legacy mantenidas para compatibilidad
def circle(t: float) -> Tuple[float, float, float]:
    """Trayectoria circular en el plano XY"""
    return (np.cos(t * 2 * np.pi), np.sin(t * 2 * np.pi), 0.0)

def lemniscate(t: float) -> Tuple[float, float, float]:
    """Lemniscata de Bernoulli (∞ horizontal)"""
    angle = t * 2 * np.pi
    scale = 1 / (1 + np.sin(angle) ** 2)
    x = scale * np.cos(angle)
    y = scale * np.sin(angle) * np.cos(angle)
    return (x, y, 0.0)

def spiral(t: float) -> Tuple[float, float, float]:
    """Espiral que se expande"""
    angle = t * 4 * np.pi
    radius = t
    return (radius * np.cos(angle), radius * np.sin(angle), 0.0)

def eight(t: float) -> Tuple[float, float, float]:
    """Figura en forma de 8"""
    angle = t * 2 * np.pi
    x = np.sin(angle)
    y = np.sin(angle) * np.cos(angle)
    return (x, y, 0.0)

def rose(t: float) -> Tuple[float, float, float]:
    """Rosa de 5 pétalos"""
    angle = t * 2 * np.pi
    k = 5
    r = np.cos(k * angle)
    x = r * np.cos(angle)
    y = r * np.sin(angle)
    return (x, y, 0.0)

def butterfly(t: float) -> Tuple[float, float, float]:
    """Curva mariposa"""
    angle = t * 12 * np.pi
    r = np.exp(np.cos(angle)) - 2 * np.cos(4 * angle) + np.sin(angle/12) ** 5
    x = r * np.cos(angle) * 0.3
    y = r * np.sin(angle) * 0.3
    return (x, y, 0.0)

def heart(t: float) -> Tuple[float, float, float]:
    """Forma de corazón"""
    angle = t * 2 * np.pi
    x = 16 * np.sin(angle) ** 3
    y = 13 * np.cos(angle) - 5 * np.cos(2*angle) - 2 * np.cos(3*angle) - np.cos(4*angle)
    return (x * 0.05, y * 0.05, 0.0)

def static(t: float) -> Tuple[float, float, float]:
    """Sin movimiento - posición estática"""
    return (0.0, 0.0, 0.0)

# Diccionario de funciones legacy
LEGACY_FUNCTIONS = {
    "lemniscate": lemniscate,
    "eight": eight,
    "rose": rose,
    "butterfly": butterfly,
    "heart": heart,
    "static": static
}

# Alias comunes
LEGACY_FUNCTIONS["figure_eight"] = eight
LEGACY_FUNCTIONS["inf"] = lemniscate
LEGACY_FUNCTIONS["infinity"] = lemniscate
LEGACY_FUNCTIONS["none"] = static
