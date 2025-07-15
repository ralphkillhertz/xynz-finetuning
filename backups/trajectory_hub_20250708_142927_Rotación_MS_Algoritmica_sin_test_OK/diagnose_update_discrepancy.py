# === diagnose_update_discrepancy.py ===
# 🔍 Debug: Por qué funciona en debug pero no en test normal
# ⚡ Encontrar la diferencia

import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub import EnhancedTrajectoryEngine

def diagnose_discrepancy():
    """Diagnosticar por qué no hay movimiento en test normal"""
    
    print("🔍 DIAGNÓSTICO: Discrepancia en update()")
    print("=" * 60)
    
    # Crear setup idéntico
    engine = EnhancedTrajectoryEngine(max_sources=2, fps=60)
    engine.create_source(0, "test_0")
    engine._positions[0] = np.array([10.0, 0.0, 0.0])
    
    macro_name = engine.create_macro("test", source_count=1)
    engine.set_macro_rotation(macro_name, center=[0,0,0], speed_x=0, speed_y=3, speed_z=0)
    
    print("✅ Setup completo")
    
    # Test 1: Verificar estado inicial
    print("\n📍 Estado inicial:")
    print(f"  Posición: {engine._positions[0]}")
    print(f"  _time: {engine._time}")
    print(f"  is_paused: {engine.is_paused() if hasattr(engine, 'is_paused') else 'N/A'}")
    
    # Test 2: Llamar update y ver qué pasa
    print("\n🔧 Llamando engine.update()...")
    
    pos_before = engine._positions[0].copy()
    
    # Ver si update retorna algo
    result = engine.update()
    
    pos_after = engine._positions[0].copy()
    
    print(f"  Posición antes: {pos_before}")
    print(f"  Posición después: {pos_after}")
    print(f"  ¿Cambió?: {not np.array_equal(pos_before, pos_after)}")
    print(f"  Resultado de update(): {type(result)}")
    
    # Test 3: Verificar el flujo de deltas manualmente
    print("\n🔍 Verificando flujo de deltas manualmente:")
    
    if 0 in engine.motion_states:
        motion = engine.motion_states[0]
        print(f"  MotionState existe: ✅")
        
        # Sincronizar posición
        motion.state.position = engine._positions[0].copy()
        
        # Obtener deltas
        deltas = motion.update_with_deltas(engine._time, 1/60.0)
        print(f"  Deltas obtenidos: {len(deltas)}")
        
        if deltas:
            for i, delta in enumerate(deltas):
                if hasattr(delta, 'position') and delta.position is not None:
                    print(f"    Delta {i}: {delta.position}")
                    print(f"    Magnitud: {np.linalg.norm(delta.position):.6f}")
        
        # Verificar componente macro_rotation
        if hasattr(motion, 'active_components') and 'macro_rotation' in motion.active_components:
            comp = motion.active_components['macro_rotation']
            print(f"\n  macro_rotation:")
            print(f"    enabled: {comp.enabled}")
            print(f"    speed_y: {comp.speed_y}")
    
    # Test 4: Ver el código de update
    print("\n🔍 Verificando método update():")
    
    # Verificar si hay condiciones que prevengan el update
    import inspect
    try:
        source = inspect.getsource(engine.update)
        
        # Buscar líneas clave
        if 'is_paused' in source:
            print("  ⚠️ update() verifica is_paused")
        if 'motion_states' not in source:
            print("  ❌ update() NO procesa motion_states")
        if 'update_with_deltas' in source:
            print("  ✅ update() llama a update_with_deltas")
        if '_positions[source_id] = ' in source and '+ delta.position' in source:
            print("  ✅ update() aplica deltas a posiciones")
        
        # Buscar return prematuro
        lines = source.split('\n')
        for i, line in enumerate(lines):
            if 'return' in line and i < len(lines) - 5:  # Return temprano
                print(f"  ⚠️ Return prematuro en línea {i}: {line.strip()}")
    except:
        print("  Error obteniendo source")
    
    # Test 5: Llamar update varias veces
    print("\n🔧 Llamando update() 5 veces más...")
    
    for i in range(5):
        engine.update()
        print(f"  Frame {i+1}: Posición = {engine._positions[0]}")

if __name__ == "__main__":
    diagnose_discrepancy()