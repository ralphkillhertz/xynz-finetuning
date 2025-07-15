# === restore_motion_components.py ===
# 🔧 Fix: Buscar backup y restaurar motion_components.py
# ⚡ EMERGENCY RESTORE

import os
import glob
from datetime import datetime

# Buscar backups
backups = glob.glob("motion_components.py.backup_*")
backups.extend(glob.glob("trajectory_hub/core/motion_components.py.backup_*"))
backups.extend(glob.glob("*.backup_*"))

if backups:
    # Ordenar por fecha
    backups.sort()
    print(f"📦 Encontrados {len(backups)} backups")
    
    # Usar el más reciente
    latest = backups[-1]
    print(f"🔄 Restaurando desde: {latest}")
    
    # Copiar
    import shutil
    shutil.copy(latest, "trajectory_hub/core/motion_components.py")
    print("✅ Restaurado")
else:
    print("❌ No hay backups disponibles")
    print("🔧 Creando motion_components.py desde cero...")
    
    # Crear versión mínima funcional
    with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
        f.write('''"""Motion components for trajectory system"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json

@dataclass
class MotionState:
    """Estado completo del movimiento de una fuente"""
    source_id: int
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    orientation: Dict[str, float] = field(default_factory=lambda: {"yaw": 0.0, "pitch": 0.0, "roll": 0.0})
    aperture: float = 0.5
    distance: float = 1.0
    
@dataclass 
class MotionDelta:
    """Cambio incremental en el estado"""
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    orientation: Dict[str, float] = field(default_factory=dict)
    aperture: float = 0.0
    distance: float = 0.0
    source_id: Optional[int] = None

class MotionComponent(ABC):
    """Componente base para todos los modificadores de movimiento"""
    
    @abstractmethod
    def update(self, current_time: float, dt: float, state: MotionState) -> MotionState:
        """Actualiza el estado del movimiento"""
        pass
        
    @abstractmethod
    def calculate_delta(self, state: MotionState, current_time: float, dt: float) -> MotionDelta:
        """Calcula el cambio incremental"""
        pass

class SourceMotion:
    """Contenedor de componentes de movimiento para una fuente"""
    
    def __init__(self, state: MotionState):
        self.state = state
        self.active_components: Dict[str, MotionComponent] = {}
        
    def update_with_deltas(self, current_time: float, dt: float) -> List[MotionDelta]:
        """Actualiza y retorna lista de deltas de todos los componentes"""
        deltas = []
        for name, component in self.active_components.items():
            if hasattr(component, 'calculate_delta'):
                delta = component.calculate_delta(self.state, current_time, dt)
                if delta and (np.any(delta.position != 0) or delta.orientation):
                    deltas.append(delta)
        return deltas

class ConcentrationComponent(MotionComponent):
    """Componente para concentrar/dispersar fuentes"""
    
    def __init__(self):
        self.target_factor = 1.0
        self.current_factor = 1.0
        self.speed = 1.0
        self.enabled = True
        
    def update(self, current_time: float, dt: float, state: MotionState) -> MotionState:
        return state
        
    def calculate_delta(self, state: MotionState, current_time: float, dt: float) -> MotionDelta:
        """Calcula delta para concentración"""
        if not self.enabled or self.current_factor == self.target_factor:
            return MotionDelta()
            
        # Interpolar factor
        diff = self.target_factor - self.current_factor
        step = min(abs(diff), self.speed * dt)
        self.current_factor += step if diff > 0 else -step
        
        # Calcular movimiento hacia/desde el origen
        delta = MotionDelta()
        delta.position = -state.position * (1 - self.current_factor) * 0.1
        delta.source_id = state.source_id
        
        return delta

class IndividualTrajectory(MotionComponent):
    """Trayectoria individual para una fuente"""
    
    def __init__(self):
        self.shape = "circle"
        self.shape_params = {"radius": 1.0}
        self.movement_mode = "stop"
        self.movement_speed = 1.0
        self.position_on_trajectory = 0.0
        self.enabled = True
        self.time_offset = 0.0
        
    def update(self, current_time: float, dt: float, state: MotionState) -> MotionState:
        """Actualiza posición en la trayectoria"""
        if self.enabled and self.movement_mode != "stop":
            self.position_on_trajectory += self.movement_speed * dt
            self.position_on_trajectory %= 1.0
        return state
        
    def calculate_delta(self, state: MotionState, current_time: float, dt: float) -> MotionDelta:
        """Calcula delta basado en la trayectoria"""
        if not self.enabled or self.movement_mode == "stop":
            return MotionDelta()
            
        # Actualizar posición en trayectoria
        self.update(current_time, dt, state)
        
        # Calcular nueva posición
        t = self.position_on_trajectory * 2 * np.pi
        
        if self.shape == "circle":
            radius = self.shape_params.get("radius", 1.0)
            new_x = radius * np.cos(t)
            new_y = radius * np.sin(t)
            new_z = 0
        else:
            new_x = new_y = new_z = 0
            
        target_pos = np.array([new_x, new_y, new_z])
        
        delta = MotionDelta()
        delta.position = target_pos - state.position
        delta.source_id = state.source_id
        
        return delta

class MacroTrajectory(MotionComponent):
    """Trayectoria para un grupo macro"""
    
    def __init__(self, trajectory_type="circle", speed=1.0):
        self.trajectory_type = trajectory_type
        self.speed = speed
        self.time = 0.0
        self.enabled = True
        self.params = {"radius": 5.0}
        
    def update(self, current_time: float, dt: float, state: MotionState) -> MotionState:
        if self.enabled:
            self.time += dt * self.speed
        return state
        
    def calculate_delta(self, state: MotionState, current_time: float, dt: float) -> MotionDelta:
        """Calcula delta para trayectoria macro"""
        if not self.enabled:
            return MotionDelta()
            
        self.update(current_time, dt, state)
        
        # Calcular posición objetivo
        t = self.time
        
        if self.trajectory_type == "circle":
            radius = self.params.get("radius", 5.0)
            target_x = radius * np.cos(t)
            target_y = radius * np.sin(t)
            target_z = 0
        else:
            target_x = target_y = target_z = 0
            
        target_pos = np.array([target_x, target_y, target_z])
        
        delta = MotionDelta()
        delta.position = (target_pos - state.position) * 0.1  # Suavizar
        delta.source_id = state.source_id
        
        return delta

class MacroRotation(MotionComponent):
    """Rotación algorítmica del macro alrededor de su centro"""
    
    def __init__(self):
        self.center = np.zeros(3)
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.speed_z = 0.0
        self.enabled = False
        
    def update_center(self, center: np.ndarray):
        """Actualiza el centro de rotación"""
        self.center = center.copy()
        
    def set_rotation(self, speed_x: float, speed_y: float, speed_z: float):
        """Configura velocidades de rotación"""
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.speed_z = speed_z
        self.enabled = any([speed_x, speed_y, speed_z])
        
    def update(self, current_time: float, dt: float, state: MotionState) -> MotionState:
        return state
        
    def calculate_delta(self, state: MotionState, current_time: float, dt: float) -> MotionDelta:
        """Calcula el cambio de posición debido a la rotación"""
        if not self.enabled:
            return MotionDelta()
            
        # Obtener posición actual
        current_pos = state.position.copy()
        
        # Trasladar al origen
        translated = current_pos - self.center
        
        # Aplicar rotaciones
        angle_y = self.speed_y * dt
        
        if abs(angle_y) > 0:
            cos_y = np.cos(angle_y)
            sin_y = np.sin(angle_y)
            new_x = translated[0] * cos_y - translated[2] * sin_y
            new_z = translated[0] * sin_y + translated[2] * cos_y
            translated[0] = new_x
            translated[2] = new_z
        
        # Trasladar de vuelta
        new_pos = translated + self.center
        
        # Calcular delta
        delta = MotionDelta()
        delta.position = new_pos - current_pos
        delta.source_id = state.source_id
        
        return delta
''')

print("\n🚀 Ejecutando test...")
os.system("python test_rotation_ms_final.py")