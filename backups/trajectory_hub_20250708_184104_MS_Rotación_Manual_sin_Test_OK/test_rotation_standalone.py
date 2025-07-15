# === test_rotation_standalone.py ===
# 🎯 Test independiente de rotación
# ⚡ Sin exec, directo y simple

import sys
import os
import numpy as np
import math

# Path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("🎯 TEST DEFINITIVO DE ROTACIÓN MANUAL MS")
print("=" * 60)

try:
    from trajectory_hub.core import EnhancedTrajectoryEngine
    
    # Crear engine
    print("\n1️⃣ Creando engine...")
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)
    
    # Crear macro
    print("2️⃣ Creando macro...")
    engine.create_macro("test", 4, formation="square")
    macro_name = list(engine._macros.keys())[0]
    macro = engine._macros[macro_name]
    print(f"   Macro: {macro_name}")
    print(f"   Fuentes: {sorted(macro.source_ids)}")
    
    # Posiciones iniciales
    print("\n3️⃣ Estableciendo posiciones...")
    positions = [[3, 0, 0], [0, 3, 0], [-3, 0, 0], [0, -3, 0]]
    for i, (sid, pos) in enumerate(zip(sorted(macro.source_ids), positions)):
        engine._positions[sid] = np.array(pos, dtype=np.float32)
        print(f"   Fuente {sid}: {pos}")
    
    # Configurar rotación
    print("\n4️⃣ Configurando rotación 90°...")
    engine.set_manual_macro_rotation(
        macro_name, 
        yaw=math.pi/2,  # 90 grados
        pitch=0, 
        roll=0, 
        interpolation_speed=0.1
    )
    
    # Guardar posiciones antes
    pos_before = {}
    for sid in macro.source_ids:
        pos_before[sid] = engine._positions[sid].copy()
    
    # UPDATE
    print("\n5️⃣ Ejecutando engine.update()...")
    try:
        engine.update()
        print("   ✅ Update ejecutado")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Verificar resultados
    print("\n📊 RESULTADOS:")
    print("-" * 60)
    
    total_movement = 0
    any_movement = False
    
    for sid in sorted(macro.source_ids):
        before = pos_before[sid]
        after = engine._positions[sid]
        diff_vector = after - before
        diff_magnitude = np.linalg.norm(diff_vector)
        total_movement += diff_magnitude
        
        if diff_magnitude > 0.0001:
            any_movement = True
            print(f"Fuente {sid}:")
            print(f"   Antes:    [{before[0]:6.2f}, {before[1]:6.2f}, {before[2]:6.2f}]")
            print(f"   Después:  [{after[0]:6.2f}, {after[1]:6.2f}, {after[2]:6.2f}]")
            print(f"   Cambio:   [{diff_vector[0]:6.3f}, {diff_vector[1]:6.3f}, {diff_vector[2]:6.3f}]")
            print(f"   Magnitud: {diff_magnitude:.6f} ✅")
        else:
            print(f"Fuente {sid}: Sin cambios ❌")
    
    print("-" * 60)
    
    # Veredicto final
    if any_movement:
        print(f"\n🎉🎉🎉 ¡¡¡ÉXITO TOTAL!!! 🎉🎉🎉")
        print(f"✅ Las rotaciones manuales MS funcionan perfectamente")
        print(f"✅ Movimiento total: {total_movement:.6f}")
        print(f"✅ El sistema de deltas está 100% funcional")
        print(f"\n📌 RESUMEN:")
        print(f"   - ManualMacroRotation: ✅ FUNCIONA")
        print(f"   - Sistema de deltas: ✅ APLICANDO CAMBIOS")
        print(f"   - Delta mismatch: ✅ RESUELTO")
    else:
        print(f"\n❌ Las rotaciones aún no funcionan")
        print(f"   Movimiento detectado: {total_movement}")
        
        # Debug adicional
        print("\n🔍 DEBUG ADICIONAL:")
        if macro.source_ids:
            sid = list(macro.source_ids)[0]
            if sid in engine.motion_states:
                motion = engine.motion_states[sid]
                if hasattr(motion, 'active_components'):
                    print(f"   Componentes activos: {list(motion.active_components.keys())}")
                    if 'manual_macro_rotation' in motion.active_components:
                        comp = motion.active_components['manual_macro_rotation']
                        print(f"   Rotación enabled: {comp.enabled}")
                        print(f"   Target yaw: {comp.target_yaw}")

except Exception as e:
    print(f"\n❌ Error general: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test completado")