#!/usr/bin/env python3
"""
🔍 DEBUG: Ver qué pasa dentro del nuevo step()
"""

import os
import sys
import numpy as np

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

print("""
================================================================================
🔍 DEBUG DEL NUEVO STEP()
================================================================================
""")

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=2, fps=60)

print("1️⃣ CREANDO MACRO...")
macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)

print("\n2️⃣ ESTADO INICIAL:")
print(f"   Posiciones: F0={engine._positions[0]}, F1={engine._positions[1]}")
print(f"   Macro ID: {macro_id}")
print(f"   Macro source_ids: {engine._macros[macro_id].source_ids}")

# Aplicar concentración
print("\n3️⃣ APLICANDO CONCENTRACIÓN...")
engine.set_macro_concentration(macro_id, 0.5)

# Verificar que concentration_factor se guardó
macro = engine._macros[macro_id]
print(f"   macro.concentration_factor = {getattr(macro, 'concentration_factor', 'NO EXISTE')}")

# Añadir prints temporales a step()
print("\n4️⃣ MODIFICANDO step() TEMPORALMENTE PARA DEBUG...")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(engine_file, 'r', encoding='utf-8') as f:
    original_content = f.read()

# Modificar step para añadir prints
debug_content = original_content

# Añadir print al inicio de step
debug_content = debug_content.replace(
    'def step(self, dt: float = None) -> dict:',
    '''def step(self, dt: float = None) -> dict:
        print("\\nDEBUG step() llamado")'''
)

# Añadir print en el loop de macros
debug_content = debug_content.replace(
    'for macro_id, macro in self._macros.items():',
    '''for macro_id, macro in self._macros.items():
            print(f"  Procesando macro {macro_id}")'''
)

# Añadir print cuando se calcula concentration
debug_content = debug_content.replace(
    'if hasattr(macro, \'concentration_factor\') and macro.concentration_factor > 0:',
    '''if hasattr(macro, 'concentration_factor') and macro.concentration_factor > 0:
                print(f"    concentration_factor = {macro.concentration_factor}")'''
)

# Añadir print cuando se calcula el centro
debug_content = debug_content.replace(
    'center = np.mean(positions, axis=0)',
    '''center = np.mean(positions, axis=0)
                    print(f"    Centro calculado: {center}")
                    print(f"    Posiciones: {positions}")'''
)

# Añadir print cuando se aplica offset
debug_content = debug_content.replace(
    'motion.concentration_offset = direction * macro.concentration_factor',
    '''motion.concentration_offset = direction * macro.concentration_factor
                            print(f"      F{sid}: offset = {motion.concentration_offset}")'''
)

# Añadir print en la actualización de positions
debug_content = debug_content.replace(
    'self._positions[sid] = pos',
    '''print(f"    F{sid}: pos_base={motion.state.position}, offset={getattr(motion, 'concentration_offset', 'NONE')}, pos_final={pos}")
                self._positions[sid] = pos'''
)

# Guardar versión con debug
with open(engine_file, 'w', encoding='utf-8') as f:
    f.write(debug_content)

# Ejecutar step con debug
print("\n5️⃣ EJECUTANDO step() CON DEBUG:")
try:
    engine.step()
except Exception as e:
    print(f"\n❌ Error en step(): {e}")
    import traceback
    traceback.print_exc()

# Verificar resultado
print("\n6️⃣ RESULTADO:")
print(f"   F0: antes={[-4., 0., 0.]}, después={engine._positions[0]}")
print(f"   F1: antes={[0., 0., 0.]}, después={engine._positions[1]}")

mov0 = np.linalg.norm(engine._positions[0] - np.array([-4., 0., 0.]))
mov1 = np.linalg.norm(engine._positions[1] - np.array([0., 0., 0.]))
print(f"\n   Movimiento: F0={mov0:.6f}, F1={mov1:.6f}")

# Restaurar archivo original
with open(engine_file, 'w', encoding='utf-8') as f:
    f.write(original_content)
print("\n✅ Archivo restaurado")

# Análisis
print("\n" + "="*80)
print("📊 ANÁLISIS")
print("="*80)

if mov0 < 0.001 and mov1 < 0.001:
    print("""
Las fuentes NO se mueven. Posibles causas:

1. concentration_factor no se está guardando en el macro
2. El loop de macros no encuentra macros con concentration_factor > 0
3. Las posiciones no se están calculando correctamente
4. motion.update() está sobrescribiendo algo

SOLUCIÓN: Implementar una versión aún más simple que no dependa
de tantas condiciones.
""")
else:
    print("\n✅ ¡Las fuentes se mueven! El debug ayudó a encontrar el problema.")