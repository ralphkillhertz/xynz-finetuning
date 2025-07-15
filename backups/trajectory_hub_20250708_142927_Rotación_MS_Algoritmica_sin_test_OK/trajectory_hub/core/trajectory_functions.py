"""
trajectory_functions.py - Biblioteca de funciones de trayectoria
"""

import numpy as np
from typing import Tuple, Callable

# Tipo de función de trayectoria
TrajectoryFunc = Callable[[float], Tuple[float, float, float]]

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

def helix(t: float) -> Tuple[float, float, float]:
    """Hélice 3D"""
    angle = t * 4 * np.pi
    return (np.cos(angle), np.sin(angle), t * 2 - 1)

def square(t: float) -> Tuple[float, float, float]:
    """Trayectoria cuadrada"""
    # Dividir en 4 segmentos
    segment = int(t * 4) % 4
    local_t = (t * 4) % 1
    
    if segment == 0:  # Derecha
        return (local_t * 2 - 1, 1.0, 0.0)
    elif segment == 1:  # Abajo
        return (1.0, 1 - local_t * 2, 0.0)
    elif segment == 2:  # Izquierda
        return (1 - local_t * 2, -1.0, 0.0)
    else:  # Arriba
        return (-1.0, local_t * 2 - 1, 0.0)

def triangle(t: float) -> Tuple[float, float, float]:
    """Trayectoria triangular"""
    segment = int(t * 3) % 3
    local_t = (t * 3) % 1
    
    if segment == 0:
        return (local_t * 2 - 1, -0.5, 0.0)
    elif segment == 1:
        return (1 - local_t, local_t * 1.5 - 0.5, 0.0)
    else:
        return (-local_t, 1 - local_t * 1.5, 0.0)

def eight(t: float) -> Tuple[float, float, float]:
    """Figura en forma de 8"""
    angle = t * 2 * np.pi
    x = np.sin(angle)
    y = np.sin(angle) * np.cos(angle)
    return (x, y, 0.0)

def infinity(t: float) -> Tuple[float, float, float]:
    """Símbolo de infinito (∞ vertical)"""
    angle = t * 2 * np.pi
    x = np.sin(angle) * np.cos(angle)
    y = np.sin(angle)
    return (x, y, 0.0)

def rose(t: float) -> Tuple[float, float, float]:
    """Rosa de 5 pétalos"""
    angle = t * 2 * np.pi
    k = 5
    r = np.cos(k * angle)
    x = r * np.cos(angle)
    y = r * np.sin(angle)
    return (x, y, 0.0)

def lissajous(t: float) -> Tuple[float, float, float]:
    """Figura de Lissajous"""
    return (np.sin(3 * t * 2 * np.pi), np.sin(2 * t * 2 * np.pi), 0.0)

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

# Diccionario de funciones disponibles
TRAJECTORY_FUNCTIONS = {
    "circle": circle,
    "lemniscate": lemniscate,
    "spiral": spiral,
    "helix": helix,
    "square": square,
    "triangle": triangle,
    "eight": eight,
    "infinity": infinity,
    "rose": rose,
    "lissajous": lissajous,
    "butterfly": butterfly,
    "heart": heart,
    "static": static
}

# Alias comunes
TRAJECTORY_FUNCTIONS["figure8"] = eight
TRAJECTORY_FUNCTIONS["figure_eight"] = eight
TRAJECTORY_FUNCTIONS["inf"] = infinity
TRAJECTORY_FUNCTIONS["none"] = static
