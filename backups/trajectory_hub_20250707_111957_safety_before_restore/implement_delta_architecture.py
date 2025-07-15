#!/usr/bin/env python3
"""
🏗️ IMPLEMENTAR ARQUITECTURA DE DELTAS
⚡ Cambiar de sobrescritura a suma de componentes
"""

import os
import shutil
from datetime import datetime
import re

print("🏗️ IMPLEMENTACIÓN DE ARQUITECTURA DE DELTAS")
print("="*60)

# Archivo principal a modificar
motion_file = "trajectory_hub/core/motion_components.py"

if not os.path.exists(motion_file):
    print(f"❌ No se encuentra {motion_file}")
    exit(1)

# Backup
backup_file = f"{motion_file}.backup_delta_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(motion_file, backup_file)
print(f"✅ Backup creado: {backup_file}")

# Leer archivo
with open(motion_file, 'r') as f:
    content = f.read()

# Buscar la clase SourceMotion y su método update
print("\n🔍 Buscando SourceMotion.update()...")

# Encontrar el método update
update_pattern = r'(class SourceMotion.*?)(def update\(self[^)]*\)[^:]*:)(.*?)((?=\n    def|\nclass|\Z))'
match = re.search(update_pattern, content, re.DOTALL)

if match:
    print("✅ Método update encontrado")
    
    # Crear nuevo método update con arquitectura de deltas
    new_update_method = '''
    def update(self, time: float, dt: float) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Update motion with DELTA ARCHITECTURE.
        Each component contributes a delta that gets summed at the end.
        """
        # Store initial state
        initial_position = self.state.position.copy()
        initial_orientation = self.state.orientation.copy()
        initial_aperture = self.state.aperture
        
        # Initialize delta accumulators
        position_deltas = []
        orientation_deltas = []
        aperture_delta = 0.0
        
        # Process each component
        for component_name, component in self.components.items():
            if not component.enabled:
                continue
                
            if component_name == 'group_behavior':
                # Skip for now (handled externally)
                continue
            
            # Save current state before component
            temp_state = MotionState(
                position=self.state.position.copy(),
                orientation=self.state.orientation.copy(),
                aperture=self.state.aperture
            )
            
            # Let component update state
            try:
                self.state = component.update(self.state, time, dt)
                
                # Calculate deltas
                pos_delta = self.state.position - temp_state.position
                ori_delta = self.state.orientation - temp_state.orientation
                aper_delta = self.state.aperture - temp_state.aperture
                
                # Store deltas if significant
                if np.any(np.abs(pos_delta) > 1e-6):
                    position_deltas.append((component_name, pos_delta))
                if np.any(np.abs(ori_delta) > 1e-6):
                    orientation_deltas.append((component_name, ori_delta))
                if abs(aper_delta) > 1e-6:
                    aperture_delta += aper_delta
                    
                # Restore state for next component
                self.state = temp_state
                
            except Exception as e:
                print(f"Component {component_name} error: {e}")
                continue
        
        # Apply all deltas (SUM)
        self.state.position = initial_position.copy()
        self.state.orientation = initial_orientation.copy()
        self.state.aperture = initial_aperture
        
        # Sum position deltas
        for comp_name, delta in position_deltas:
            self.state.position += delta
            
        # Sum orientation deltas
        for comp_name, delta in orientation_deltas:
            self.state.orientation += delta
            
        # Apply aperture delta
        self.state.aperture += aperture_delta
        
        # Apply safety limits
        self.state.position = np.clip(self.state.position, -50, 50)
        self.state.aperture = np.clip(self.state.aperture, 0.0, 1.0)
        
        # Normalize orientation to [-π, π]
        self.state.orientation = np.mod(self.state.orientation + np.pi, 2*np.pi) - np.pi
        
        return self.state.position, self.state.orientation, self.state.aperture'''
    
    # Reemplazar el método update
    new_content = content[:match.start(2)] + new_update_method + content[match.end(3):]
    
    # Guardar cambios
    with open(motion_file, 'w') as f:
        f.write(new_content)
    
    print("✅ Método update reemplazado con arquitectura de deltas")
    
else:
    print("❌ No se encontró el método update")
    exit(1)

# Crear script de test
print("\n📝 Creando script de test...")

test_script = '''#!/usr/bin/env python3
"""
🧪 TEST DE ARQUITECTURA DE DELTAS
"""

import sys
import numpy as np
sys.path.append('.')

from trajectory_hub.core.motion_components import SourceMotion, MotionState

print("🧪 TEST DE SUMA DE COMPONENTES")
print("="*60)

# Crear motion de prueba
motion = SourceMotion(source_id=0)
motion.state.position = np.array([0.0, 0.0, 0.0])

# Crear componentes de prueba
class TestComponent:
    def __init__(self, name, delta_pos):
        self.enabled = True
        self.name = name
        self.delta_pos = np.array(delta_pos)
    
    def update(self, state, time, dt):
        new_state = MotionState(
            position=state.position + self.delta_pos,
            orientation=state.orientation.copy(),
            aperture=state.aperture
        )
        return new_state

# Agregar múltiples componentes
motion.components['comp1'] = TestComponent('comp1', [1.0, 0.0, 0.0])
motion.components['comp2'] = TestComponent('comp2', [0.0, 2.0, 0.0])
motion.components['comp3'] = TestComponent('comp3', [0.0, 0.0, 3.0])

print(f"Posición inicial: {motion.state.position}")
print("\\nComponentes:")
print("  comp1: delta = [1, 0, 0]")
print("  comp2: delta = [0, 2, 0]")
print("  comp3: delta = [0, 0, 3]")

# Update
pos, ori, aper = motion.update(0.0, 0.016)

print(f"\\nPosición final: {pos}")
print(f"Esperado: [1, 2, 3]")

# Verificar
expected = np.array([1.0, 2.0, 3.0])
if np.allclose(pos, expected):
    print("\\n✅ ¡ÉXITO! Los componentes se SUMAN correctamente")
else:
    print("\\n❌ Error: Los componentes no se suman")

# Test con componente deshabilitado
print("\\n" + "-"*60)
print("Test con comp2 deshabilitado:")
motion.components['comp2'].enabled = False
motion.state.position = np.array([0.0, 0.0, 0.0])

pos, ori, aper = motion.update(0.0, 0.016)
print(f"Posición final: {pos}")
print(f"Esperado: [1, 0, 3]")

expected_disabled = np.array([1.0, 0.0, 3.0])
if np.allclose(pos, expected_disabled):
    print("\\n✅ Componente deshabilitado correctamente ignorado")
else:
    print("\\n❌ Problema con componente deshabilitado")

print("\\n✅ Test completado")
'''

with open('test_delta_architecture.py', 'w') as f:
    f.write(test_script)
os.chmod('test_delta_architecture.py', 0o755)

print("✅ Script de test creado: test_delta_architecture.py")

# Resumen
print("\n" + "="*60)
print("📊 RESUMEN DE CAMBIOS")
print("="*60)
print("""
ARQUITECTURA ANTERIOR (Secuencial):
  - Cada componente modifica el estado directamente
  - El último componente sobrescribe los anteriores
  - position = component3(component2(component1(initial)))

ARQUITECTURA NUEVA (Deltas):
  - Cada componente calcula su delta independientemente
  - Todos los deltas se suman al final
  - position = initial + Δ1 + Δ2 + Δ3

BENEFICIOS:
  ✅ Componentes independientes
  ✅ Efectos se suman en lugar de sobrescribir
  ✅ Fácil agregar/quitar componentes
  ✅ Comportamiento predecible
""")

print("\n🧪 Para probar: python test_delta_architecture.py")
print(f"⏮️ Para revertir: cp {backup_file} {motion_file}")