# === debug_rotation_final.py ===
# 🔍 Debug final: Rastrear rotaciones paso a paso
# ⚡ Usando la API correcta

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import math

print("🔍 DEBUG FINAL: Sistema de Rotaciones")
print("=" * 60)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=4, fps=60, enable_modulator=False)

# Crear macro directamente (esto crea las fuentes)
print("🔧 Creando macro con 2 fuentes...")
macro_name = engine.create_macro("square", source_count=2)
print(f"✅ Macro creado: {macro_name}")

# Obtener información del macro
if macro_name in engine._macros:
    macro = engine._macros[macro_name]
    source_ids = list(macro.source_ids)
    print(f"   Fuentes en el macro: {source_ids}")
else:
    print("❌ Macro no encontrado")
    exit(1)

# Establecer posiciones iniciales
print("\n📍 Estableciendo posiciones iniciales:")
positions = [
    np.array([3.0, 0.0, 0.0]),   # Eje X
    np.array([0.0, 3.0, 0.0])    # Eje Y
]

for sid, pos in zip(source_ids, positions):
    engine._positions[sid] = pos.copy()
    print(f"   Fuente {sid}: {pos}")

# Verificar motion_states
print("\n🔍 Verificando motion_states:")
for sid in source_ids:
    if sid in engine.motion_states:
        motion = engine.motion_states[sid]
        print(f"   Fuente {sid}:")
        print(f"      - Existe: ✅")
        print(f"      - Components: {list(motion.active_components.keys())}")
        print(f"      - State position: {motion.state.position}")
    else:
        print(f"   Fuente {sid}: ❌ No existe motion_state")

# Configurar rotación manual
print("\n🔧 Configurando rotación manual de 90°...")
try:
    engine.set_manual_macro_rotation(
        macro_name,
        yaw=math.pi/2,
        pitch=0.0,
        roll=0.0,
        interpolation_speed=0.5
    )
    print("✅ Rotación configurada")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Verificar componentes después de configurar
print("\n🔍 Verificando componentes después de configurar:")
for sid in source_ids[:1]:  # Solo verificar la primera
    if sid in engine.motion_states:
        motion = engine.motion_states[sid]
        print(f"   Components: {list(motion.active_components.keys())}")
        
        if 'manual_macro_rotation' in motion.active_components:
            comp = motion.active_components['manual_macro_rotation']
            print("   ✅ manual_macro_rotation configurado:")
            print(f"      - enabled: {comp.enabled}")
            print(f"      - target_yaw: {math.degrees(comp.target_yaw):.1f}°")
            print(f"      - center: {comp.center}")
            
            # Test directo
            print("\n   🧪 Test directo de calculate_delta:")
            delta = comp.calculate_delta(motion.state, 0.0, 1/60.0)
            if delta:
                print(f"      ✅ Delta: {delta.position}")
            else:
                print("      ❌ Delta es None")

# Ejecutar updates y rastrear
print("\n⚙️ Ejecutando updates y rastreando cambios:")
print("-" * 50)

for update_num in range(5):
    print(f"\nUpdate {update_num + 1}:")
    
    # Guardar posiciones antes
    pos_antes = {sid: engine._positions[sid].copy() for sid in source_ids}
    
    # Sincronizar states manualmente antes del update
    for sid in source_ids:
        if sid in engine.motion_states:
            engine.motion_states[sid].state.position = engine._positions[sid].copy()
    
    # Ejecutar update
    engine.update()
    
    # Verificar cambios
    any_change = False
    for sid in source_ids:
        pos_despues = engine._positions[sid]
        cambio = pos_despues - pos_antes[sid]
        magnitud = np.linalg.norm(cambio)
        
        if magnitud > 0.0001:
            any_change = True
            print(f"   Fuente {sid}: cambió {magnitud:.6f}")
            print(f"      Antes:   {pos_antes[sid]}")
            print(f"      Después: {pos_despues}")
        else:
            print(f"   Fuente {sid}: SIN cambio")
    
    if not any_change:
        print("   ⚠️ Ninguna fuente se movió")

# Análisis del problema
print("\n" + "=" * 60)
print("🔍 ANÁLISIS DEL CÓDIGO:")

# Verificar si engine.update procesa motion_states
import inspect
update_code = inspect.getsource(engine.update)

print("\n1. ¿engine.update() procesa motion_states?")
if "motion_states" in update_code:
    print("   ✅ SÍ menciona motion_states")
    
    # Buscar qué hace con ellos
    lines = update_code.split('\n')
    for i, line in enumerate(lines):
        if "motion.update" in line or "motion_states" in line:
            print(f"   Línea {i}: {line.strip()}")
else:
    print("   ❌ NO menciona motion_states")

print("\n2. ¿Se aplican deltas?")
if "delta" in update_code.lower():
    print("   ✅ SÍ menciona deltas")
else:
    print("   ❌ NO menciona deltas")

# Test manual del proceso completo
print("\n🧪 TEST MANUAL DEL PROCESO:")
if source_ids:
    sid = source_ids[0]
    if sid in engine.motion_states:
        motion = engine.motion_states[sid]
        
        # Sincronizar state
        motion.state.position = engine._positions[sid].copy()
        print(f"State sincronizado: {motion.state.position}")
        
        # Llamar update manualmente
        if hasattr(motion, 'update'):
            dt = 1/60.0
            result = motion.update(engine._time, dt)
            print(f"motion.update() retornó: {result}")
            
            # Si retorna algo, aplicarlo
            if result is not None:
                print(f"Tipo de resultado: {type(result)}")
                
                # Si es MotionState, aplicar la posición
                if hasattr(result, 'position'):
                    print(f"Nueva posición del state: {result.position}")
                    # Aplicar manualmente
                    engine._positions[sid] = result.position
                    print(f"Posición actualizada manualmente: {engine._positions[sid]}")

print("\n💡 CONCLUSIÓN:")
print("El problema parece estar en cómo engine.update() procesa los resultados de motion.update()")