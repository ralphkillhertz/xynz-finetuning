# === debug_no_movement_fixed.py ===
# 🔍 Debug: Por qué no hay movimiento en rotaciones (CORREGIDO)
# ⚡ Rastrear el flujo completo de deltas

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import math

print("🔍 DEBUG: Por qué no hay movimiento")
print("=" * 60)

# Crear engine mínimo
engine = EnhancedTrajectoryEngine(max_sources=2, fps=60, enable_modulator=False)

# Crear fuente primero
sid = engine.create_source(0)
print(f"✅ Fuente creada: {sid}")

# Establecer posición
engine._positions[sid] = np.array([3.0, 0.0, 0.0])
print(f"📍 Posición inicial: {engine._positions[sid]}")

# Crear macro
macro_name = engine.create_macro("square", source_count=1)
print(f"✅ Macro creado: {macro_name}")

# Verificar motion_states
print(f"\n🔍 Motion states existe para fuente {sid}: {sid in engine.motion_states}")
if sid in engine.motion_states:
    motion = engine.motion_states[sid]
    print(f"   Active components: {list(motion.active_components.keys())}")
    print(f"   State position: {motion.state.position}")

# Configurar rotación
print("\n🔧 Configurando rotación 90°...")
try:
    engine.set_manual_macro_rotation(
        macro_name,
        yaw=math.pi/2,
        interpolation_speed=0.5
    )
    print("✅ Rotación configurada")
except Exception as e:
    print(f"❌ Error configurando rotación: {e}")

# Verificar que se configuró
print("\n🔍 Verificando configuración:")
if sid in engine.motion_states:
    motion = engine.motion_states[sid]
    print(f"   Components después de configurar: {list(motion.active_components.keys())}")
    
    if 'manual_macro_rotation' in motion.active_components:
        comp = motion.active_components['manual_macro_rotation']
        print(f"   ✅ manual_macro_rotation existe:")
        print(f"      - enabled: {comp.enabled}")
        print(f"      - target_yaw: {comp.target_yaw:.3f} rad ({math.degrees(comp.target_yaw):.1f}°)")
        print(f"      - current_yaw: {comp.current_yaw:.3f}")
        print(f"      - center: {comp.center}")
        print(f"      - interpolation_speed: {comp.interpolation_speed}")
    else:
        print("   ❌ manual_macro_rotation NO existe")

# Test directo del componente
print("\n🧪 Test directo del componente:")
if sid in engine.motion_states and 'manual_macro_rotation' in engine.motion_states[sid].active_components:
    motion = engine.motion_states[sid]
    comp = motion.active_components['manual_macro_rotation']
    
    # Probar calculate_delta
    print("   Probando calculate_delta:")
    state = motion.state
    delta = comp.calculate_delta(state, 0.0, 1/60.0)
    
    if delta:
        print(f"   ✅ Delta calculado: {delta.position}")
        print(f"      Magnitud: {np.linalg.norm(delta.position):.6f}")
    else:
        print("   ❌ Delta es None")

# Rastrear update
print("\n⚙️ Ejecutando engine.update()...")
pos_antes = engine._positions[sid].copy()
print(f"   Posición antes: {pos_antes}")

# Ejecutar varios updates
for i in range(5):
    engine.update()
    pos_despues = engine._positions[sid]
    cambio = pos_despues - pos_antes
    print(f"   Update {i+1}: pos={pos_despues}, cambio={cambio}, magnitud={np.linalg.norm(cambio):.6f}")
    pos_antes = pos_despues.copy()

# Verificar el método update del engine
print("\n🔍 Analizando engine.update():")
import inspect
try:
    update_source = inspect.getsource(engine.update)
    
    # Buscar líneas clave
    key_patterns = [
        "motion_states",
        "motion.update",
        "calculate_delta",
        "update_with_deltas",
        "_positions[",
        "state.position"
    ]
    
    print("   Buscando patrones clave en update():")
    for pattern in key_patterns:
        if pattern in update_source:
            print(f"   ✅ Contiene '{pattern}'")
            # Mostrar las líneas relevantes
            lines = update_source.split('\n')
            for i, line in enumerate(lines):
                if pattern in line:
                    print(f"      Línea {i}: {line.strip()}")
        else:
            print(f"   ❌ NO contiene '{pattern}'")
            
except Exception as e:
    print(f"   Error analizando update: {e}")

# Verificar si motion.update existe y qué hace
print("\n🔍 Analizando SourceMotion.update():")
if sid in engine.motion_states:
    motion = engine.motion_states[sid]
    if hasattr(motion, 'update'):
        print("   ✅ motion.update existe")
        try:
            # Ver qué retorna
            result = motion.update(0.0, 1/60.0)
            print(f"   update() retornó: {result}")
            print(f"   Tipo: {type(result)}")
        except Exception as e:
            print(f"   Error llamando update: {e}")
    else:
        print("   ❌ motion.update NO existe")

# Diagnóstico final
print("\n" + "=" * 60)
print("📋 DIAGNÓSTICO FINAL:")
print("-" * 40)

# Verificar sistema de deltas
if sid in engine.motion_states:
    motion = engine.motion_states[sid]
    
    # ¿Existe update_with_deltas?
    if hasattr(motion, 'update_with_deltas'):
        print("✅ Sistema de deltas parece estar implementado")
        print("   - motion.update_with_deltas existe")
        
        # Probar
        deltas = motion.update_with_deltas(0.0, 1/60.0)
        if deltas:
            print(f"   - Retorna {len(deltas)} deltas")
        else:
            print("   - Retorna lista vacía o None")
    else:
        print("❌ Sistema de deltas puede no estar completo")
        print("   - motion.update_with_deltas NO existe")

print("\n💡 Posibles causas del problema:")
print("1. El sistema de deltas no está integrado en engine.update()")
print("2. Los deltas se calculan pero no se aplican")
print("3. Hay un problema con la sincronización de states")
print("4. El componente no está habilitado correctamente")