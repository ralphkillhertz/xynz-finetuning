# === diagnose_rotation_issue.py ===
# 🔍 Diagnóstico: Por qué las rotaciones manuales no funcionan
# ⚡ Verificar cada paso del proceso de rotación

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import math

print("🔍 DIAGNÓSTICO: Rotaciones Manuales")
print("=" * 60)

# Crear engine simple
engine = EnhancedTrajectoryEngine(max_sources=2, fps=60, enable_modulator=False)

# Crear macro con solo 2 fuentes
macro_name = engine.create_macro("square", source_count=2)
macro = engine._macros[macro_name]
source_ids = list(macro.source_ids)

# Posiciones iniciales simples
positions = [
    np.array([3.0, 0.0, 0.0]),   # En el eje X positivo
    np.array([0.0, 3.0, 0.0])    # En el eje Y positivo
]

print("📍 Configurando posiciones iniciales:")
for sid, pos in zip(source_ids, positions):
    engine._positions[sid] = pos
    if sid in engine.motion_states:
        engine.motion_states[sid].state.position = pos.copy()
    print(f"   Fuente {sid}: {pos}")

# Configurar rotación
print("\n🔧 Configurando rotación de 90 grados...")
engine.set_manual_macro_rotation(
    macro_name,
    yaw=math.pi/2,  # 90 grados
    pitch=0.0,
    roll=0.0,
    interpolation_speed=0.5  # Muy rápido para test
)

# Verificar que el componente existe
print("\n🔍 Verificando componentes:")
for sid in source_ids:
    if sid in engine.motion_states:
        motion = engine.motion_states[sid]
        print(f"\n   Fuente {sid}:")
        print(f"   - motion_states existe: ✅")
        print(f"   - active_components: {list(motion.active_components.keys())}")
        
        if 'manual_macro_rotation' in motion.active_components:
            comp = motion.active_components['manual_macro_rotation']
            print(f"   - manual_macro_rotation existe: ✅")
            print(f"   - enabled: {comp.enabled}")
            print(f"   - target_yaw: {comp.target_yaw:.3f} rad ({math.degrees(comp.target_yaw):.1f}°)")
            print(f"   - current_yaw: {comp.current_yaw:.3f} rad")
            print(f"   - center: {comp.center}")
            
            # Probar calculate_delta directamente
            print("\n   🧪 Probando calculate_delta directamente:")
            state = motion.state
            delta = comp.calculate_delta(state, 0.0, 1/60.0)
            if delta:
                print(f"   - Delta calculado: {delta.position}")
                print(f"   - Magnitud delta: {np.linalg.norm(delta.position):.6f}")
            else:
                print(f"   - Delta es None ❌")
        else:
            print(f"   - manual_macro_rotation NO existe ❌")

# Ejecutar UN solo update
print("\n⚙️ Ejecutando UN update...")
old_positions = {sid: engine._positions[sid].copy() for sid in source_ids}

# Verificar qué hace engine.update()
print("\n🔍 Rastreando engine.update():")
engine.update()

# Ver cambios
print("\n📊 Cambios después de update:")
for sid in source_ids:
    old_pos = old_positions[sid]
    new_pos = engine._positions[sid]
    diff = new_pos - old_pos
    
    print(f"\n   Fuente {sid}:")
    print(f"   - Posición anterior: {old_pos}")
    print(f"   - Posición nueva:    {new_pos}")
    print(f"   - Diferencia:        {diff}")
    print(f"   - Magnitud cambio:   {np.linalg.norm(diff):.6f}")
    
    # Verificar el state
    if sid in engine.motion_states:
        state_pos = engine.motion_states[sid].state.position
        print(f"   - State position:    {state_pos}")
        print(f"   - State sincronizado: {'✅' if np.allclose(state_pos, new_pos) else '❌'}")

# Test manual del proceso completo
print("\n🧪 Test manual del proceso de rotación:")
if source_ids and source_ids[0] in engine.motion_states:
    sid = source_ids[0]
    motion = engine.motion_states[sid]
    
    if 'manual_macro_rotation' in motion.active_components:
        comp = motion.active_components['manual_macro_rotation']
        
        # Estado inicial
        print(f"\n   Estado inicial:")
        print(f"   - Posición: {engine._positions[sid]}")
        print(f"   - Current yaw: {comp.current_yaw:.3f}")
        print(f"   - Target yaw: {comp.target_yaw:.3f}")
        
        # Simular varios pasos
        for i in range(5):
            # Calcular delta
            state = motion.state
            state.position = engine._positions[sid].copy()  # Asegurar sincronización
            
            delta = comp.calculate_delta(state, i/60.0, 1/60.0)
            
            if delta and np.linalg.norm(delta.position) > 0.0001:
                print(f"\n   Paso {i+1}:")
                print(f"   - Delta: {delta.position}")
                print(f"   - Current yaw antes: {comp.current_yaw:.3f}")
                
                # Aplicar delta manualmente
                engine._positions[sid] += delta.position
                motion.state.position = engine._positions[sid].copy()
                
                print(f"   - Nueva posición: {engine._positions[sid]}")
                print(f"   - Current yaw después: {comp.current_yaw:.3f}")
            else:
                print(f"\n   Paso {i+1}: Sin movimiento (delta muy pequeño o None)")

# Diagnóstico final
print("\n" + "=" * 60)
print("📋 DIAGNÓSTICO FINAL:")
print("-" * 40)

# Verificar método update de SourceMotion
print("\n🔍 Verificando SourceMotion.update:")
if source_ids and source_ids[0] in engine.motion_states:
    motion = engine.motion_states[source_ids[0]]
    
    # Verificar si el método update existe
    if hasattr(motion, 'update'):
        print("   - Método update existe: ✅")
        
        # Ver qué hace update
        import inspect
        update_code = inspect.getsource(motion.update)
        if "active_components" in update_code:
            print("   - update procesa active_components: ✅")
        else:
            print("   - update NO procesa active_components: ❌")
    else:
        print("   - Método update NO existe: ❌")

print("\n💡 Posibles problemas:")
print("   1. El componente no se está agregando correctamente")
print("   2. El delta no se está calculando")
print("   3. El engine.update() no está aplicando deltas")
print("   4. Hay un problema con la sincronización de states")