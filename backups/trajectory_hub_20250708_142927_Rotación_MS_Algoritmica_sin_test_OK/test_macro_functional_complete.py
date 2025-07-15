# === test_macro_functional_complete.py ===
# 🧪 Test funcional REAL de MacroTrajectory
# ⚡ Verificar que TODO funcione de verdad

import numpy as np
import time
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 TEST FUNCIONAL COMPLETO: MacroTrajectory\n")

# 1. CREAR ENGINE
print("1️⃣ CREANDO ENGINE...")
try:
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    print("✅ Engine creado")
    print(f"  - max_sources: {engine.max_sources}")
    print(f"  - fps: {engine.fps}")
    print(f"  - _macros existe: {hasattr(engine, '_macros')}")
except Exception as e:
    print(f"❌ Error creando engine: {e}")
    exit(1)

# 2. CREAR MACRO
print("\n2️⃣ CREANDO MACRO...")
try:
    # Intentar crear macro
    result = engine.create_macro("test_group", 5)
    print(f"✅ create_macro retornó: {result}")
    
    # Verificar que se guardó
    if hasattr(engine, '_macros'):
        macros_keys = list(engine._macros.keys())
        print(f"  - Macros guardados: {macros_keys}")
        
        if result in engine._macros or "test_group" in engine._macros:
            print("  ✅ Macro SÍ se guardó")
            macro_key = result if result in engine._macros else "test_group"
            macro = engine._macros[macro_key]
            print(f"  - source_ids: {macro.source_ids}")
            print(f"  - trajectory_component: {hasattr(macro, 'trajectory_component')}")
        else:
            print("  ❌ Macro NO se guardó")
            print("  ❌ FALLO CRÍTICO: create_macro no funciona")
            exit(1)
    else:
        print("  ❌ _macros no existe")
        exit(1)
        
except Exception as e:
    print(f"❌ Error creando macro: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# 3. VERIFICAR MOTION_STATES
print("\n3️⃣ VERIFICANDO MOTION_STATES...")
try:
    print(f"  - motion_states keys: {list(engine.motion_states.keys())}")
    
    # Verificar que las fuentes tengan macro_trajectory
    components_ok = 0
    for sid in macro.source_ids:
        if sid in engine.motion_states:
            components = list(engine.motion_states[sid].active_components.keys())
            has_macro = "macro_trajectory" in components
            print(f"  - Fuente {sid}: {components} {'✅' if has_macro else '❌'}")
            if has_macro:
                components_ok += 1
    
    if components_ok == len(macro.source_ids):
        print("  ✅ Todas las fuentes tienen macro_trajectory")
    else:
        print(f"  ❌ Solo {components_ok}/{len(macro.source_ids)} fuentes configuradas")
        
except Exception as e:
    print(f"❌ Error verificando motion_states: {e}")

# 4. CONFIGURAR TRAYECTORIA
print("\n4️⃣ CONFIGURANDO TRAYECTORIA CIRCULAR...")
try:
    # Definir trayectoria
    def circular_trajectory(t):
        radius = 5.0
        return np.array([
            radius * np.cos(t),
            radius * np.sin(t),
            0.0
        ])
    
    # Aplicar
    engine.set_macro_trajectory(macro_key, circular_trajectory)
    print("✅ Trayectoria configurada")
    
    # Verificar que se activó
    if macro.trajectory_component:
        print(f"  - trajectory_component.enabled: {macro.trajectory_component.enabled}")
        print(f"  - trajectory_func existe: {macro.trajectory_component.trajectory_func is not None}")
except Exception as e:
    print(f"❌ Error configurando trayectoria: {e}")
    import traceback
    traceback.print_exc()

# 5. TEST DE MOVIMIENTO
print("\n5️⃣ TEST DE MOVIMIENTO (2 segundos)...")
try:
    # Guardar posiciones iniciales
    initial_positions = {}
    for sid in macro.source_ids:
        initial_positions[sid] = engine._positions[sid].copy()
        print(f"  - Fuente {sid} inicial: {initial_positions[sid]}")
    
    # Ejecutar simulación
    print("\n  Ejecutando frames...")
    start_time = time.time()
    frames = 0
    
    while time.time() - start_time < 2.0:
        engine.update()
        frames += 1
        
        # Mostrar progreso cada 30 frames
        if frames % 30 == 0:
            pos = engine._positions[macro.source_ids[0]]
            dist = np.linalg.norm(pos - initial_positions[macro.source_ids[0]])
            print(f"    Frame {frames}: distancia = {dist:.3f}")
    
    print(f"\n  Total frames: {frames}")
    
    # Verificar movimiento final
    print("\n  RESULTADOS FINALES:")
    total_movement = 0
    for sid in macro.source_ids:
        final_pos = engine._positions[sid]
        distance = np.linalg.norm(final_pos - initial_positions[sid])
        total_movement += distance
        
        status = "✅" if distance > 0.1 else "❌"
        print(f"  {status} Fuente {sid}: movió {distance:.3f} unidades")
        if distance > 0:
            print(f"     De: {initial_positions[sid]}")
            print(f"     A:  {final_pos}")
    
    avg_movement = total_movement / len(macro.source_ids)
    
    if avg_movement > 0.1:
        print(f"\n✅ ÉXITO: Movimiento promedio = {avg_movement:.3f} unidades")
        print("\n🎉 MacroTrajectory FUNCIONA CORRECTAMENTE")
    else:
        print(f"\n❌ FALLO: Movimiento promedio = {avg_movement:.6f} unidades")
        print("❌ Las fuentes NO se mueven")
        
except Exception as e:
    print(f"❌ Error en test de movimiento: {e}")
    import traceback
    traceback.print_exc()

# 6. DIAGNÓSTICO ADICIONAL
print("\n6️⃣ DIAGNÓSTICO ADICIONAL:")
try:
    # Verificar calculate_delta
    if macro.trajectory_component and hasattr(macro.trajectory_component, 'calculate_delta'):
        print("✅ MacroTrajectory tiene calculate_delta")
        
        # Probar calculate_delta directamente
        if macro.source_ids:
            sid = macro.source_ids[0]
            if sid in engine.motion_states:
                motion = engine.motion_states[sid]
                delta = macro.trajectory_component.calculate_delta(motion, 1.0, 1/60)
                if delta:
                    print(f"✅ calculate_delta retorna: {delta.position}")
                else:
                    print("❌ calculate_delta retorna None")
    else:
        print("❌ MacroTrajectory NO tiene calculate_delta")
        
except Exception as e:
    print(f"Error en diagnóstico: {e}")

print("\n" + "="*60)
print("📊 RESUMEN DEL TEST:")
print("="*60)