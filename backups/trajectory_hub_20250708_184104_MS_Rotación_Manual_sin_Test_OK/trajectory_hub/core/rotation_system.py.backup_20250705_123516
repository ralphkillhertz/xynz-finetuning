#!/usr/bin/env python3
"""
Sistema de Rotación Algorítmica para Trajectory Hub
Proporciona patrones de rotación dinámicos para macros y trayectorias
"""

import numpy as np
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class RotationPattern:
    """Clase base para patrones de rotación algorítmica"""
    
    AVAILABLE_PATTERNS = ["circular", "figure8", "spiral", "wobble", "pendulum"]
    
    def __init__(self, pattern_type: str = "circular"):
        if pattern_type not in self.AVAILABLE_PATTERNS:
            raise ValueError(f"Patrón '{pattern_type}' no válido")
            
        self.pattern_type = pattern_type
        self.speed = 1.0
        self.amplitude = 1.0
        self.phase_offset = 0.0
        self.time_offset = 0.0
        
    def set_parameters(self, speed: float = 1.0, amplitude: float = 1.0, 
                      phase_offset: float = 0.0):
        """Configurar parámetros del patrón"""
        self.speed = speed
        self.amplitude = amplitude
        self.phase_offset = phase_offset
        
    def calculate_rotation(self, time: float) -> Tuple[float, float, float]:
        """Calcular ángulos de rotación según el patrón"""
        phase = (time + self.time_offset) * self.speed + self.phase_offset
        
        if self.pattern_type == "circular":
            pitch = np.sin(phase) * 0.3 * self.amplitude
            yaw = np.cos(phase) * 0.5 * self.amplitude
            roll = np.sin(phase * 2) * 0.2 * self.amplitude
            
        elif self.pattern_type == "figure8":
            pitch = np.sin(phase) * 0.4 * self.amplitude
            yaw = np.sin(phase * 2) * 0.5 * self.amplitude
            roll = np.cos(phase * 3) * 0.15 * self.amplitude
            
        elif self.pattern_type == "spiral":
            radius = 0.1 + (phase % (2 * np.pi)) / (2 * np.pi)
            pitch = np.sin(phase) * radius * 0.3 * self.amplitude
            yaw = np.cos(phase) * radius * 0.5 * self.amplitude
            roll = phase * 0.05 * self.amplitude
            
        elif self.pattern_type == "wobble":
            pitch = np.sin(phase * 1.7) * 0.25 * self.amplitude
            yaw = np.sin(phase * 2.3) * 0.35 * self.amplitude
            roll = np.sin(phase * 3.1) * 0.15 * self.amplitude
            
        elif self.pattern_type == "pendulum":
            pitch = np.sin(phase) * 0.5 * self.amplitude
            yaw = 0.0
            roll = np.sin(phase * 0.5) * 0.2 * self.amplitude
        else:
            pitch = yaw = roll = 0.0
            
        return pitch, yaw, roll
    
    def get_rotation_matrix(self, time: float) -> np.ndarray:
        """Obtener matriz de rotación 3x3"""
        pitch, yaw, roll = self.calculate_rotation(time)
        
        # Matrices de rotación
        cx, sx = np.cos(pitch), np.sin(pitch)
        rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
        
        cy, sy = np.cos(yaw), np.sin(yaw)
        ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
        
        cz, sz = np.cos(roll), np.sin(roll)
        rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
        
        return rz @ ry @ rx


class MacroRotation:
    """Rotación algorítmica para macros"""
    
    def __init__(self):
        self.pattern = RotationPattern()
        self.center = np.zeros(3)
        self.active = False
        self.start_time = 0.0
        
    def set_pattern(self, pattern_type: str, **params):
        """Configurar el patrón"""
        self.pattern = RotationPattern(pattern_type)
        self.pattern.set_parameters(**params)
        self.active = True
        
    def apply_to_positions(self, positions: np.ndarray, time: float) -> np.ndarray:
        """Aplicar rotación a posiciones"""
        if not self.active:
            return positions
            
        if np.allclose(self.center, 0):
            self.center = np.mean(positions, axis=0)
        
        rotation_matrix = self.pattern.get_rotation_matrix(time - self.start_time)
        
        rotated_positions = np.zeros_like(positions)
        for i, pos in enumerate(positions):
            rel_pos = pos - self.center
            rotated_pos = rotation_matrix @ rel_pos
            rotated_positions[i] = self.center + rotated_pos
            
        return rotated_positions
    
    def start(self, time: float):
        self.start_time = time
        self.active = True
        
    def stop(self):
        self.active = False


class TrajectoryRotation:
    """Rotación algorítmica para trayectorias individuales"""
    
    def __init__(self):
        self.pattern = RotationPattern()
        self.active = False
        self.start_time = 0.0
        
    def set_pattern(self, pattern_type: str, **params):
        """Configurar el patrón"""
        self.pattern = RotationPattern(pattern_type)
        self.pattern.set_parameters(**params)
        self.active = True
        
    def get_rotation_matrix(self, time: float) -> np.ndarray:
        """Obtener matriz de rotación"""
        if not self.active:
            return np.eye(3)
            
        return self.pattern.get_rotation_matrix(time - self.start_time)
    
    def start(self, time: float):
        self.start_time = time
        self.active = True
        
    def stop(self):
        self.active = False
