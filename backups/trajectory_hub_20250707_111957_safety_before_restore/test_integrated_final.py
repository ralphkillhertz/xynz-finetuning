#!/usr/bin/env python3
"""
🧪 TEST INTEGRADO FINAL
"""

import os
import sys
import numpy as np

# Path setup
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("\n🧪 TEST FINAL INTEGRADO\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)

# Crear macro
macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=5.0)

# Guardar posiciones iniciales
print("📍 POSICIONES INICIALES:")
initial_positions = {}
for sid in range(4):
    if sid in engine._source_motions:
        pos = engine._source_motions[sid].state.position.copy()
        initial_positions[sid] = pos
        print(f"   Fuente {sid}: {pos}")

# Calcular centro esperado
center = np.mean(list(initial_positions.values()), axis=0)
print(f"\n📍 Centro del macro: {center}")

# Aplicar concentración
factor = 0.3
print(f"\n🎯 Aplicando concentración factor={factor}...")
engine.set_macro_concentration(macro_id, factor)

# Verificar offsets
print("\n🔍 OFFSETS APLICADOS:")
has_offsets = False
for sid in range(4):
    if sid in engine._source_motions:
        motion = engine._source_motions[sid]
        offset = motion.concentration_offset
        mag = np.linalg.norm(offset)
        if mag > 0:
            has_offsets = True
        print(f"   Fuente {sid}: offset={offset}, magnitud={mag:.4f}")

if not has_offsets:
    print("\n❌ ERROR: Los offsets siguen en cero")
    sys.exit(1)

# Ejecutar simulación
print("\n🔄 EJECUTANDO 100 FRAMES...")
for i in range(100):
    engine.step()
    
    if (i + 1) % 25 == 0:
        # Mostrar progreso
        pos0 = engine._positions[0] if hasattr(engine, '_positions') else engine._source_motions[0].get_position()
        print(f"   Frame {i+1}: Fuente 0 en {pos0}")

# Calcular resultados
print("\n📊 RESULTADOS FINALES:")
total_movement = 0
final_positions = {}

for sid in initial_positions:
    # Obtener posición final
    if hasattr(engine._source_motions[sid], 'get_position'):
        final_pos = engine._source_motions[sid].get_position()
    else:
        final_pos = engine._positions[sid]
    
    final_positions[sid] = final_pos
    movement = np.linalg.norm(final_pos - initial_positions[sid])
    total_movement += movement
    
    print(f"   Fuente {sid}:")
    print(f"      Inicial: {initial_positions[sid]}")
    print(f"      Final:   {final_pos}")
    print(f"      Movimiento: {movement:.4f}")

# Verificar concentración
initial_dispersion = np.std(list(initial_positions.values()))
final_dispersion = np.std(list(final_positions.values()))

print(f"\n📊 ANÁLISIS DE CONCENTRACIÓN:")
print(f"   Dispersión inicial: {initial_dispersion:.4f}")
print(f"   Dispersión final:   {final_dispersion:.4f}")
print(f"   Reducción:          {(1 - final_dispersion/initial_dispersion)*100:.1f}%")

if total_movement > 0.1:
    print(f"\n✅ ¡ÉXITO! Las fuentes se movieron")
    if final_dispersion < initial_dispersion:
        print("✅ ¡LA CONCENTRACIÓN FUNCIONA!")
        print("\n🚀 Ahora prueba el controlador interactivo:")
        print("   python trajectory_hub/interface/interactive_controller.py")
else:
    print(f"\n❌ Las fuentes no se movieron lo suficiente")

print("\n" + "="*60)
