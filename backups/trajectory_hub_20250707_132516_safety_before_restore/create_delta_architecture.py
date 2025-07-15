#!/usr/bin/env python3
"""
🏗️ CREAR ARQUITECTURA DE DELTAS - Sistema Paralelo
Fase 1: Establecer la base para composición de movimientos
"""

import os
import shutil
from datetime import datetime

print("""
================================================================================
🏗️ CREANDO ARQUITECTURA DE DELTAS
================================================================================
Este script:
1. Crea las clases base para el sistema de deltas
2. Modifica SourceMotion para usar composición
3. Prepara el sistema para migración gradual
================================================================================
""")

# 1. Crear backup
backup_name = f"trajectory_hub_backup_delta_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
print(f"📦 Creando backup: {backup_name}")
shutil.copytree("trajectory_hub", backup_name)
print("✅ Backup creado\n")

# 2. Crear archivo base para deltas
delta_base_code = '''"""
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
'''

# Guardar archivo de deltas
delta_file = "trajectory_hub/core/delta_system.py"
print(f"📝 Creando {delta_file}...")
with open(delta_file, 'w') as f:
    f.write(delta_base_code)
print("✅ Sistema de deltas creado\n")

# 3. Modificar motion_components.py para incluir el sistema
motion_file = "trajectory_hub/core/motion_components.py"
print(f"📝 Actualizando {motion_file}...")

# Leer archivo actual
with open(motion_file, 'r') as f:
    content = f.read()

# Añadir import al principio
if "from trajectory_hub.core.delta_system import" not in content:
    import_pos = content.find("import numpy as np")
    if import_pos > 0:
        next_line = content.find("\n", import_pos) + 1
        new_import = "from trajectory_hub.core.delta_system import MotionDelta, MotionComponent, DeltaComposer\n"
        content = content[:next_line] + new_import + content[next_line:]

# Modificar SourceMotion para preparar sistema de deltas
source_motion_start = content.find("class SourceMotion:")
if source_motion_start > 0:
    # Buscar el __init__ de SourceMotion
    init_start = content.find("def __init__(self", source_motion_start)
    init_end = content.find("\n\n", init_start)
    
    # Añadir sistema de componentes al final del __init__
    if "self.motion_components" not in content[init_start:init_end]:
        indent = "        "
        delta_init = f'''
{indent}# Sistema de componentes para arquitectura de deltas
{indent}self.motion_components = {{}}  # Dict[str, MotionComponent]
{indent}self.component_weights = {{}}  # Pesos para cada componente
{indent}self.use_delta_system = False  # Flag para migración gradual
'''
        # Insertar antes del final del __init__
        content = content[:init_end] + delta_init + content[init_end:]

# Guardar cambios
with open(motion_file, 'w') as f:
    f.write(content)
print("✅ SourceMotion preparado para deltas\n")

# 4. Crear script de migración para siguiente fase
migration_script = '''#!/usr/bin/env python3
"""
🔄 MIGRAR COMPONENTES A SISTEMA DE DELTAS
Fase 2: Convertir cada componente uno por uno
"""

import os

print("""
================================================================================
🔄 MIGRACIÓN DE COMPONENTES
================================================================================
Orden de migración recomendado:
1. ConcentrationComponent (más simple)
2. TrajectoryComponent (IS)
3. RotationComponent (MS)
4. ModulationComponent (3D)

Ejecutar: python migrate_concentration_to_delta.py
================================================================================
""")
'''

with open("migrate_to_delta_system.py", 'w') as f:
    f.write(migration_script)
os.chmod("migrate_to_delta_system.py", 0o755)

print("""
================================================================================
✅ FASE 1 COMPLETADA - ARQUITECTURA DE DELTAS CREADA
================================================================================

CAMBIOS REALIZADOS:
1. ✅ Creado trajectory_hub/core/delta_system.py
   - Clase MotionDelta para cambios incrementales
   - Clase abstracta MotionComponent
   - DeltaComposer para composición
   
2. ✅ Modificado SourceMotion
   - Añadido sistema de componentes
   - Flag use_delta_system para migración gradual
   - Preparado para composición paralela

3. ✅ Backup creado: {0}

PRÓXIMO PASO:
Ejecutar la migración del primer componente:
python migrate_concentration_to_delta.py

================================================================================
""".format(backup_name))