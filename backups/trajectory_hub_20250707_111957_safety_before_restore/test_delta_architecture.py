#!/usr/bin/env python3
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
print("\nComponentes:")
print("  comp1: delta = [1, 0, 0]")
print("  comp2: delta = [0, 2, 0]")
print("  comp3: delta = [0, 0, 3]")

# Update
pos, ori, aper = motion.update(0.0, 0.016)

print(f"\nPosición final: {pos}")
print(f"Esperado: [1, 2, 3]")

# Verificar
expected = np.array([1.0, 2.0, 3.0])
if np.allclose(pos, expected):
    print("\n✅ ¡ÉXITO! Los componentes se SUMAN correctamente")
else:
    print("\n❌ Error: Los componentes no se suman")

# Test con componente deshabilitado
print("\n" + "-"*60)
print("Test con comp2 deshabilitado:")
motion.components['comp2'].enabled = False
motion.state.position = np.array([0.0, 0.0, 0.0])

pos, ori, aper = motion.update(0.0, 0.016)
print(f"Posición final: {pos}")
print(f"Esperado: [1, 0, 3]")

expected_disabled = np.array([1.0, 0.0, 3.0])
if np.allclose(pos, expected_disabled):
    print("\n✅ Componente deshabilitado correctamente ignorado")
else:
    print("\n❌ Problema con componente deshabilitado")

print("\n✅ Test completado")
