# === fix_motion_components_complete.py ===
# 🔧 Fix: Reorganizar motion_components.py completamente
# ⚡ MEGA FIX

import os

# Leer archivo actual
with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar si hay imports al principio
if not content.startswith('"""') and not content.startswith('import') and not content.startswith('from'):
    # Necesitamos añadir imports
    imports = '''"""Motion components for trajectory system"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json

'''
    content = imports + content

# Verificar que las clases base estén definidas primero
if 'class MotionState' not in content:
    # Añadir clases base
    base_classes = '''
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

'''
    # Insertar después de los imports
    import_end = content.find('\n\n')
    if import_end > 0:
        content = content[:import_end+2] + base_classes + content[import_end+2:]
    else:
        content = imports + base_classes + content

# Guardar versión corregida
with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ motion_components.py reorganizado")

# Verificar sintaxis
import py_compile
try:
    py_compile.compile("trajectory_hub/core/motion_components.py", doraise=True)
    print("✅ Sintaxis correcta")
    os.system("python test_rotation_ms_final.py")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔧 Aplicando fix adicional...")
    os.system("python fix_motion_final_cleanup.py")