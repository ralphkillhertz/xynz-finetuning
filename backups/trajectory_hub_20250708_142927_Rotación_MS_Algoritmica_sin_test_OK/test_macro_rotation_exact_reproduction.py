# === test_macro_rotation_exact_reproduction.py ===
# 🎯 Test: Reproducir EXACTAMENTE el flujo que funcionó
# ⚡ Basado en diagnose_update_discrepancy.py

import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub import EnhancedTrajectoryEngine

def test_exact_reproduction():
    """Reproducir exactamente el flujo del diagnóstico exitoso"""
    
    print("🎯 REPRODUCCIÓN EXACTA del diagnóstico exitoso")
    print("=" * 60)
    
    # Setup IDÉNTICO al diagnóstico
    engine = EnhancedTrajectoryEngine(max_sources=2, fps=60)
    engine.create_source(0, "test_0")
    engine._positions[0] = np.array([10.0, 0.0, 0.0])
    
    macro_name = engine.create_macro("test", source_count=1)
    engine.set_macro_rotation(macro_name, center=[0,0,0], speed_x=0, speed_y=3, speed_z=0)
    
    print("✅ Setup completo")
    
    # PASO CLAVE: Verificar flujo de deltas manualmente ANTES del primer update
    print("\n🔍 Verificando flujo de deltas manualmente (como en el diagnóstico):")
    
    if 0 in engine.motion_states:
        motion = engine.motion_states[0]
        
        # Sincronizar posición
        motion.state.position = engine._positions[0].copy()
        
        # Obtener deltas
        deltas = motion.update_with_deltas(engine._time, 1/60.0)
        print(f"  Deltas obtenidos: {len(deltas)}")
        
        if deltas:
            for delta in deltas:
                if hasattr(delta, 'position') and delta.position is not None:
                    print(f"  Delta: {delta.position}")
    
    # AHORA sí, llamar update()
    print("\n🔧 Llamando engine.update() 5 veces...")
    
    for i in range(5):
        engine.update()
        pos = engine._positions[0]
        print(f"  Frame {i+1}: Posición = {pos}")
    
    # Verificar resultado
    pos_final = engine._positions[0]
    pos_inicial = np.array([10.0, 0.0, 0.0])
    dist = np.linalg.norm(pos_final - pos_inicial)
    
    print(f"\n📊 RESULTADO:")
    print(f"  Distancia recorrida: {dist:.3f}")
    print(f"  ¿Funciona?: {'✅ SÍ' if dist > 1.0 else '❌ NO'}")
    
    # Si funciona, investigar por qué
    if dist > 1.0:
        print("\n💡 ANÁLISIS:")
        print("  El llamado manual a update_with_deltas ANTES del primer update()")
        print("  parece 'activar' algo que permite el movimiento.")
        print("\n  Posibles causas:")
        print("  1. Sincronización de state.position")
        print("  2. Inicialización de algún estado interno")
        print("  3. Activación del componente")
        
        # Probar teoría
        print("\n🔍 PRUEBA: Crear nueva fuente SIN llamar update_with_deltas...")
        
        engine2 = EnhancedTrajectoryEngine(max_sources=2, fps=60)
        engine2.create_source(1, "test_1")
        engine2._positions[1] = np.array([0.0, 0.0, 10.0])
        
        macro2 = engine2.create_macro("test2", source_count=1)
        engine2.set_macro_rotation(macro2, center=[0,0,0], speed_x=0, speed_y=3, speed_z=0)
        
        # NO llamar update_with_deltas manualmente
        
        # Directamente update
        for i in range(3):
            engine2.update()
        
        dist2 = np.linalg.norm(engine2._positions[1] - np.array([0.0, 0.0, 10.0]))
        print(f"\n  Resultado sin llamada manual: dist = {dist2:.3f}")
        print(f"  {'❌ NO funciona sin la llamada manual' if dist2 < 0.1 else '✅ SÍ funciona'}")
    
    return dist > 1.0

if __name__ == "__main__":
    success = test_exact_reproduction()
    
    if success:
        print("\n" + "="*60)
        print("🔧 SOLUCIÓN ENCONTRADA:")
        print("  Necesitamos sincronizar state.position antes del primer update")
        print("  O asegurar que update() lo haga automáticamente")