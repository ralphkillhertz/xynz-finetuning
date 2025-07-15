#!/usr/bin/env python3
"""
🧪 TEST FINAL: ¿Funciona la concentración?
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

print("""
================================================================================
🧪 TEST FINAL DE CONCENTRACIÓN
================================================================================
""")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)

# Crear macro con fuentes dispersas
print("📊 CREANDO MACRO...")
macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=6.0)

# Guardar posiciones iniciales
print("\n📍 POSICIONES INICIALES:")
initial_positions = {}
for sid in range(4):
    pos = engine._positions[sid].copy()
    initial_positions[sid] = pos
    print(f"   Fuente {sid}: {pos}")

# Calcular centro
center = np.mean(list(initial_positions.values()), axis=0)
print(f"\n📍 Centro del macro: {center}")

# Aplicar concentración
factor = 0.3
print(f"\n🎯 APLICANDO CONCENTRACIÓN factor={factor}...")
engine.set_macro_concentration(macro_id, factor)

# Verificar offsets
print("\n🔍 VERIFICANDO OFFSETS:")
offsets_ok = True
for sid in range(4):
    if sid in engine._source_motions:
        motion = engine._source_motions[sid]
        offset = motion.concentration_offset
        mag = np.linalg.norm(offset)
        print(f"   Fuente {sid}: offset magnitud = {mag:.4f}")
        if mag < 0.01:
            offsets_ok = False

if not offsets_ok:
    print("\n❌ ERROR: Offsets no calculados")
    sys.exit(1)

# Ejecutar simulación
print("\n🔄 EJECUTANDO SIMULACIÓN...")
print("   (Si no hay movimiento, el problema está en update/step)")

# Intentar diferentes métodos de actualización
movements = []

# Método 1: step()
if hasattr(engine, 'step'):
    print("\n   Método: step()")
    for i in range(30):
        engine.step()
        if i == 0:
            # Verificar movimiento después del primer frame
            pos0_after = engine._positions[0]
            mov = np.linalg.norm(pos0_after - initial_positions[0])
            print(f"   Movimiento después de 1 frame: {mov:.6f}")
            if mov > 0:
                print("   ✅ step() funciona!")

# Método 2: update()
elif hasattr(engine, 'update'):
    print("\n   Método: update()")
    for i in range(30):
        engine.update(engine.dt)
        if i == 0:
            pos0_after = engine._positions[0]
            mov = np.linalg.norm(pos0_after - initial_positions[0])
            print(f"   Movimiento después de 1 frame: {mov:.6f}")
            if mov > 0:
                print("   ✅ update() funciona!")

# Verificar posiciones finales
print("\n📍 POSICIONES FINALES:")
for sid in range(4):
    final_pos = engine._positions[sid]
    movement = np.linalg.norm(final_pos - initial_positions[sid])
    movements.append(movement)
    print(f"   Fuente {sid}: {final_pos}")
    print(f"      Movimiento total: {movement:.4f}")

# Análisis
avg_movement = np.mean(movements)
initial_dispersion = np.std(list(initial_positions.values()))
final_positions = [engine._positions[i] for i in range(4)]
final_dispersion = np.std(final_positions)

print(f"\n📊 ANÁLISIS:")
print(f"   Movimiento promedio: {avg_movement:.4f}")
print(f"   Dispersión inicial: {initial_dispersion:.4f}")
print(f"   Dispersión final: {final_dispersion:.4f}")

if avg_movement > 0.1:
    reduction = (1 - final_dispersion/initial_dispersion) * 100
    print(f"   Reducción dispersión: {reduction:.1f}%")
    print("\n✅ ¡ÉXITO! LA CONCENTRACIÓN FUNCIONA")
    print("\n🚀 Ahora puedes usar:")
    print("   python trajectory_hub/interface/interactive_controller.py")
else:
    print("\n❌ Las fuentes NO se movieron")
    print("\n🔧 APLICACIÓN MANUAL DE OFFSETS...")
    
    # Probar aplicación manual
    for sid in range(4):
        if sid in engine._source_motions:
            motion = engine._source_motions[sid]
            manual_pos = motion.state.position + motion.concentration_offset
            print(f"   Fuente {sid}:")
            print(f"      Posición base: {motion.state.position}")
            print(f"      Offset: {motion.concentration_offset}")
            print(f"      Posición manual: {manual_pos}")
            print(f"      _positions actual: {engine._positions[sid]}")
    
    print("\n💡 Si las posiciones manuales son diferentes,")
    print("   el problema está en update() línea 1253")
    
    # Mostrar qué hacer
    print("\n🔨 SOLUCIÓN MANUAL:")
    print("   Edita enhanced_trajectory_engine.py")
    print("   Busca la línea 1253 (self._positions[sid] = pos)")
    print("   Y asegúrate que use get_position() o sume los offsets")

print("\n" + "="*80)