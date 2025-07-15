#!/usr/bin/env python3
"""
🧪 Test Final: Sistema de Deltas y Concentración
⚡ Objetivo: Verificar que TODO funcione
🎯 Meta: Concentración moviendo las fuentes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import time

def main():
    print("🚀 TEST FINAL DEL SISTEMA DE DELTAS")
    print("=" * 60)
    
    # Imports
    print("\n1️⃣ Importando componentes...")
    try:
        from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
        from trajectory_hub.core.motion_components import (
            MotionState, MotionDelta, SourceMotion, ConcentrationComponent
        )
        print("✅ Todos los imports exitosos")
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        return
    
    # Crear engine
    print("\n2️⃣ Creando engine...")
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    print(f"✅ Engine creado (max_sources={engine.max_sources}, fps={engine.fps})")
    
    # Crear macro
    print("\n3️⃣ Creando macro con 5 fuentes...")
    source_ids = list(range(5))
    engine.create_macro("test_concentration", source_ids)
    
    # Verificar motion_states
    print(f"\n4️⃣ Motion states: {list(engine.motion_states.keys())}")
    if not engine.motion_states:
        print("⚠️ Creando motion_states manualmente...")
        for sid in source_ids:
            engine.motion_states[sid] = SourceMotion(sid)
        print(f"✅ Motion states creados: {list(engine.motion_states.keys())}")
    
    # Posiciones iniciales en círculo
    print("\n5️⃣ Estableciendo posiciones iniciales...")
    radius = 10.0
    for i in source_ids:
        angle = i * 2 * np.pi / len(source_ids)
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = 0.0
        engine._positions[i] = np.array([x, y, z])
        print(f"   Source {i}: [{x:6.2f}, {y:6.2f}, {z:6.2f}]")
    
    # Calcular métricas iniciales
    positions = [engine._positions[i] for i in source_ids]
    center = np.mean(positions, axis=0)
    distances = [np.linalg.norm(pos - center) for pos in positions]
    avg_distance_initial = np.mean(distances)
    print(f"\n📊 Centro inicial: [{center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}]")
    print(f"📏 Distancia promedio inicial: {avg_distance_initial:.2f}")
    
    # Aplicar concentración
    print("\n6️⃣ Aplicando concentración (factor=0.8)...")
    try:
        result = engine.set_macro_concentration("test_concentration", factor=0.8)
        if result:
            print("✅ Concentración aplicada exitosamente")
        else:
            print("❌ Fallo al aplicar concentración")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Simular movimiento
    print("\n7️⃣ Simulando 30 frames...")
    print("   Frame | Distancia | Cambio")
    print("   ------|-----------|--------")
    
    for frame in range(30):
        # Step
        engine.step()
        
        # Mostrar progreso cada 5 frames
        if frame % 5 == 0:
            positions = [engine._positions[i] for i in source_ids]
            center = np.mean(positions, axis=0)
            distances = [np.linalg.norm(pos - center) for pos in positions]
            avg_distance = np.mean(distances)
            change = avg_distance - avg_distance_initial
            
            status = "✅" if change < -0.1 else "⚠️"
            print(f"   {frame:5d} | {avg_distance:9.2f} | {change:+7.2f} {status}")
    
    # Resultado final
    print("\n8️⃣ RESULTADO FINAL:")
    positions_final = [engine._positions[i] for i in source_ids]
    center_final = np.mean(positions_final, axis=0)
    distances_final = [np.linalg.norm(pos - center_final) for pos in positions_final]
    avg_distance_final = np.mean(distances_final)
    
    total_change = avg_distance_final - avg_distance_initial
    percentage_change = (total_change / avg_distance_initial) * 100
    
    print(f"\n📊 Distancia inicial: {avg_distance_initial:.2f}")
    print(f"📊 Distancia final:   {avg_distance_final:.2f}")
    print(f"📊 Cambio total:      {total_change:.2f} ({percentage_change:+.1f}%)")
    
    if total_change < -0.5:
        print("\n✅ ¡ÉXITO! El sistema de concentración con deltas FUNCIONA")
        print("🎉 Las fuentes se están concentrando correctamente")
    else:
        print("\n❌ El sistema NO está funcionando correctamente")
        print("   Las fuentes no se están moviendo hacia el centro")
        
        # Debug adicional
        print("\n🔍 Debug:")
        for sid in source_ids[:2]:  # Solo las primeras 2 fuentes
            if sid in engine.motion_states:
                motion = engine.motion_states[sid]
                print(f"\n   Source {sid}:")
                print(f"     Componentes activos: {len(motion.active_components)}")
                for comp in motion.active_components:
                    print(f"       - {comp.__class__.__name__}")

if __name__ == "__main__":
    main()