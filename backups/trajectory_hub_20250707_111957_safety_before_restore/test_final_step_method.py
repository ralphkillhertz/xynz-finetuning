#!/usr/bin/env python3
"""
🧪 TEST FINAL - Verificar que step() actualiza las fuentes
"""

import os
import sys
import numpy as np

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

print("🧪 TEST FINAL DE ENGINE.STEP()\n")

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # Crear engine y macro
    engine = EnhancedTrajectoryEngine()
    macro_id = engine.create_macro("test", source_count=4, formation="grid", spacing=3.0)
    
    print("✅ Macro creado con 4 fuentes en grid")
    
    if hasattr(engine, '_source_motions'):
        motions = engine._source_motions
        
        # Posiciones iniciales
        print("\n📍 POSICIONES INICIALES:")
        positions_before = {}
        center = np.zeros(3)
        
        for source_id, motion in motions.items():
            pos = motion.state.position.copy()
            positions_before[source_id] = pos
            center += pos
            print(f"   Fuente {source_id}: {pos}")
        
        center /= len(motions)
        print(f"\n   Centro calculado: {center}")
        
        # Aplicar concentración fuerte
        print("\n🎯 APLICANDO CONCENTRACIÓN (factor 0.05 - muy concentrado)...")
        engine.set_macro_concentration(macro_id, 0.05)
        
        # Llamar step() como lo haría el controller
        print("\n🔄 LLAMANDO ENGINE.STEP() 20 VECES...")
        for i in range(20):
            state = engine.step()
            
            if i == 0:
                print(f"\n   step() devuelve: {type(state).__name__}")
                if isinstance(state, dict):
                    print(f"   Claves: {list(state.keys())}")
        
        # Posiciones finales
        print("\n📍 POSICIONES FINALES:")
        all_moved = True
        total_movement = 0
        
        for source_id, motion in motions.items():
            pos = motion.state.position
            before = positions_before[source_id]
            
            movement = np.linalg.norm(pos - before)
            total_movement += movement
            
            print(f"   Fuente {source_id}: {pos}")
            
            if movement > 0.1:
                print(f"      ✅ Se movió {movement:.2f} unidades hacia el centro")
            else:
                print(f"      ⚠️  Movimiento pequeño: {movement:.4f}")
                if movement < 0.01:
                    all_moved = False
        
        # Verificar concentración
        final_center = np.zeros(3)
        for motion in motions.values():
            final_center += motion.state.position
        final_center /= len(motions)
        
        spread_before = np.mean([np.linalg.norm(p - center) for p in positions_before.values()])
        spread_after = np.mean([np.linalg.norm(m.state.position - final_center) for m in motions.values()])
        
        print(f"\n📊 ANÁLISIS DE CONCENTRACIÓN:")
        print(f"   Dispersión inicial: {spread_before:.2f}")
        print(f"   Dispersión final: {spread_after:.2f}")
        print(f"   Reducción: {(1 - spread_after/spread_before)*100:.1f}%")
        
        if spread_after < spread_before * 0.5:
            print("\n🎉 ¡CONCENTRACIÓN FUNCIONA PERFECTAMENTE!")
            print("   Las fuentes se concentraron significativamente")
        elif spread_after < spread_before:
            print("\n✅ La concentración funciona")
            print("   Las fuentes se acercaron al centro")
        else:
            print("\n❌ La concentración NO funciona")
    
    print("\n✅ Test completado")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("🚀 Si las fuentes se concentraron, entonces:")
print("   python trajectory_hub/interface/interactive_controller.py")
print("\n🎯 ¡La concentración debería verse en Spat!")
